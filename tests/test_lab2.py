import runpy
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch

from src.controller import Controller
from src.database import RegistrationDatabase
from src.external_service import Sender, SimulatedSender
from src.user_interaction import ConsoleUserInput, UserInput
from src.validator import RegistrationValidator


PASSWORD = "Абвг12!"


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.database = RegistrationDatabase(":memory:")
        self.user = Mock(spec=UserInput)
        self.sender = Mock(spec=Sender)
        self.validator = RegistrationValidator()
        self.controller = Controller(self.user, self.validator, self.database, self.sender)

    def tearDown(self):
        self.database.close()

    def test_new_registration_is_saved_and_sent(self):
        self.user.get_registration_data.return_value = ("alex123", PASSWORD, PASSWORD)

        result = self.controller.run()

        self.assertTrue(result[0])
        self.assertEqual(result, (True, ""))
        self.assertEqual(self.database.get_record("alex123", PASSWORD, PASSWORD), result)
        self.sender.send.assert_called_once_with("Регистрация успешна")

    def test_cached_result_does_not_trigger_validation_again(self):
        """при повторе результат читается из БД."""
        self.user.get_registration_data.return_value = ("cache123", PASSWORD, PASSWORD)
        with patch.object(self.validator, "validate", wraps=self.validator.validate) as validator_spy:
            first_result = self.controller.run()
            second_result = self.controller.run()

        self.assertEqual(first_result, second_result)
        validator_spy.assert_called_once_with("cache123", PASSWORD, PASSWORD)
        self.assertEqual(self.sender.send.call_count, 2)

    def test_invalid_registration_is_persisted_and_sent_as_failure(self):
        self.user.get_registration_data.return_value = ("valid123", PASSWORD, "Абвг13!")

        result = self.controller.run()

        self.assertFalse(result[0])
        self.assertTrue(result[1])
        self.assertEqual(self.database.get_record("valid123", PASSWORD, "Абвг13!"), result)
        self.sender.send.assert_called_once_with("Регистрация отклонена: " + result[1])

    def test_warning_is_saved_separately_and_read_from_cache(self):
        self.user.get_registration_data.return_value = ("UPPERCASE", PASSWORD, PASSWORD)

        first = self.controller.run()
        with patch.object(self.validator, "validate", side_effect=AssertionError("No validation")):
            second = self.controller.run()

        self.assertTrue(first[0])
        self.assertNotEqual(first[1], "")
        self.assertEqual(first, second)
        self.sender.send.assert_called_with("Регистрация успешна: " + first[1])
        raw = self.database._connection.execute(
            "SELECT error_message, warning_message FROM registrations"
        ).fetchone()
        self.assertEqual(raw, ("", first[1]))

    def test_deleting_record_forces_recalculation(self):
        """удаление -> повторная валидация."""
        self.user.get_registration_data.return_value = ("removed123", PASSWORD, PASSWORD)
        with patch.object(self.validator, "validate", wraps=self.validator.validate) as validator_spy:
            self.controller.run()
            self.assertTrue(self.database.delete_record("removed123", PASSWORD, PASSWORD))
            self.assertIsNone(self.database.get_record("removed123", PASSWORD, PASSWORD))
            self.controller.run()

        self.assertEqual(validator_spy.call_count, 2)

    def test_key_includes_confirmation_and_password(self):
        """уникальность по всем трём полям"""
        values = [
            ("identity123", PASSWORD, PASSWORD),
            ("identity123", PASSWORD, "Абвг13!"),
            ("identity123", "Абвг13!", "Абвг13!"),
        ]
        self.user.get_registration_data.side_effect = values

        results = [self.controller.run() for _ in values]

        self.assertTrue(results[0][0])
        self.assertFalse(results[1][0])
        self.assertTrue(results[2][0])
        self.assertEqual(
            self.database._connection.execute("SELECT COUNT(*) FROM registrations").fetchone()[0],
            3,
        )


class ModuleIsolationTests(unittest.TestCase):
    def test_console_uses_input_three_times(self):
        with patch("builtins.input", side_effect=["person123", PASSWORD, PASSWORD]) as fake_input:
            data = ConsoleUserInput().get_registration_data()

        self.assertEqual(data, ("person123", PASSWORD, PASSWORD))
        self.assertEqual(fake_input.call_args_list, [
            call("Логин: "), call("Пароль: "), call("Подтверждение пароля: ")
        ])

    def test_external_sender_only_simulates_sending(self):
        sender = SimulatedSender()
        self.assertEqual(sender.sent_messages, [])
        sender.send("Запрос получен")
        sender.send("Выполнено")
        self.assertEqual(sender.sent_messages, ["Запрос получен", "Выполнено"])

    def test_validator_delegates_to_lab_1(self):
        with patch("src.validator.validate_registration", return_value=(True, "Сообщение")) as lab1_stub:
            result = RegistrationValidator().validate("person123", "pw", "confirmation")

        self.assertEqual(result, (True, "Сообщение"))
        lab1_stub.assert_called_once_with("person123", "pw", "confirmation")

    def test_abstract_interfaces_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            UserInput()
        with self.assertRaises(TypeError):
            Sender()

    def test_controller_dependencies_in_isolation(self):
        """проверка передачи управления между интерфейсами."""
        user = Mock(spec=UserInput)
        user.get_registration_data.return_value = ("five55", "pw", "pw")
        validator = Mock(spec=RegistrationValidator)
        validator.validate.return_value = (False, "Ошибка-заглушка")
        database = Mock(spec=RegistrationDatabase)
        database.get_record.return_value = None
        sender = Mock(spec=Sender)

        result = Controller(user, validator, database, sender).run()

        self.assertEqual(result, (False, "Ошибка-заглушка"))
        database.add_record.assert_called_once_with("five55", "pw", "pw", result)
        sender.send.assert_called_once_with("Регистрация отклонена: Ошибка-заглушка")


class DatabaseTests(unittest.TestCase):
    def test_nonexistent_record_does_not_delete(self):
        db = RegistrationDatabase(":memory:")
        try:
            self.assertIsNone(db.get_record("missing", "pwd", "pwd"))
            self.assertFalse(db.delete_record("missing", "pwd", "pwd"))
        finally:
            db.close()

    def test_sqlite_data_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registration.sqlite3"
            first_db = RegistrationDatabase(path)
            try:
                first_db.add_record("persist123", PASSWORD, PASSWORD, (True, ""))
            finally:
                first_db.close()

            second_db = RegistrationDatabase(path)
            try:
                self.assertEqual(second_db.get_record("persist123", PASSWORD, PASSWORD), (True, ""))
                self.assertTrue(second_db.delete_record("persist123", PASSWORD, PASSWORD))
                self.assertIsNone(second_db.get_record("persist123", PASSWORD, PASSWORD))
            finally:
                second_db.close()


class ApplicationTests(unittest.TestCase):
    def test_main_executes_full_flow_with_fake_input_and_database(self):
        from main import main

        db = RegistrationDatabase(":memory:")
        with patch("main.RegistrationDatabase", return_value=db), \
             patch("builtins.input", side_effect=["entry123", PASSWORD, PASSWORD]), \
             patch("builtins.print") as fake_print:
            main()

        fake_print.assert_any_call("Успех")
        fake_print.assert_any_call("Имитация отправки:", "Регистрация успешна")
        with self.assertRaises(sqlite3.ProgrammingError):  # main() closes its DB connection
            db.get_record("entry123", PASSWORD, PASSWORD)

    def test_main_prints_failed_status_and_message(self):
        from main import main

        db = RegistrationDatabase(":memory:")
        with patch("main.RegistrationDatabase", return_value=db), \
             patch("builtins.input", side_effect=["entry123", PASSWORD, "different"]), \
             patch("builtins.print") as fake_print:
            main()

        fake_print.assert_any_call("Ошибка")
        fake_print.assert_any_call("Пароль и подтверждение пароля не совпадают")


    def test_script_runs_as_main(self):
        original_connect = sqlite3.connect
        script = Path(__file__).resolve().parents[1] / "main.py"
        with patch(
            "src.database.sqlite3.connect",
            side_effect=lambda path: original_connect(":memory:"),
        ), patch(
            "builtins.input", side_effect=["script123", PASSWORD, PASSWORD]
        ), patch("builtins.print") as fake_print:
            runpy.run_path(str(script), run_name="__main__")

        fake_print.assert_any_call("Успех")
        fake_print.assert_any_call("Имитация отправки:", "Регистрация успешна")


if __name__ == "__main__":
    unittest.main()
