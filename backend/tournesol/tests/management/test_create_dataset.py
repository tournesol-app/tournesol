import shutil
from collections import ChainMap
from io import StringIO
from pathlib import Path
from tempfile import gettempdir

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone


@override_settings(
    MEDIA_ROOT=gettempdir(),
    APP_TOURNESOL=ChainMap({"DATASETS_BUILD_DIR": "ts_api_test_datasets"}, settings.APP_TOURNESOL),
)
class CreateDatasetTestCase(TestCase):
    def setUp(self):
        self.dataset_base_name = settings.APP_TOURNESOL["DATASET_BASE_NAME"]

    def tearDown(self):
        """
        Delete the temporary directory created by the call to the mgmt command
        `create_dataset`.
        """
        try:
            shutil.rmtree(Path(gettempdir()).joinpath("ts_api_test_datasets"))
        except FileNotFoundError:
            pass

    def test_cmd_create_new_file(self):
        """
        A call to `create_dataset` should:
            - create the `DATASETS_BUILD_DIR` if it doesn't exist
            - create exactly one dataset
        """
        output = StringIO()
        today = timezone.localdate().strftime("%Y%m%d")

        # The datasets' dir should not exist by default.
        datasets_dir = Path(gettempdir()).joinpath("ts_api_test_datasets")
        self.assertFalse(datasets_dir.exists())

        call_command("create_dataset", stdout=output)
        output_str = output.getvalue()

        datasets = list(datasets_dir.iterdir())

        # The datasets' dir should exist now.
        self.assertTrue(datasets_dir.exists())
        # Exactly one dataset has been created.
        self.assertEqual(len(datasets), 1)
        # The dataset should have been created with the expected name.
        self.assertEqual(datasets[0].name, f"{self.dataset_base_name}{today}")

        # The archive path should appear in the logs.
        archive_path = datasets_dir.joinpath(f"{self.dataset_base_name}{today}")
        self.assertIn(f"archive created at {archive_path}", output_str)
        self.assertIn("success", output_str)

    def test_cmd_delete_old_files_default(self):
        """
        Without any option, the `create_dataset` command should keep only the
        10 most recent files in the `DATASETS_BUILD_DIR`.
        """
        output = StringIO()
        today = timezone.localdate().strftime("%Y%m%d")
        datasets_dir = Path(gettempdir()).joinpath("ts_api_test_datasets")
        datasets_dir.mkdir()

        for num in range(20):
            datasets_dir.joinpath(f"{self.dataset_base_name}{num}").write_text("test")

        datasets = list(datasets_dir.iterdir())
        self.assertEqual(len(datasets), 20)

        call_command("create_dataset", stdout=output)
        archive_path = datasets_dir.joinpath(f"{self.dataset_base_name}{today}")
        output_str = output.getvalue()

        # The new dataset should have been created.
        self.assertTrue(archive_path.exists())

        # 10 datasets should have been kept by default
        datasets = list(datasets_dir.iterdir())
        self.assertEqual(len(datasets), 10)

        # The deleted archives should appear in the logs.
        self.assertEqual(output_str.count("deleted old"), 11)
        self.assertIn("success", output_str)

    def test_cmd_keep_only_option(self):
        """
        With the --keep-only option, the `create_dataset` command should keep
        only the specified number of recent files in the `DATASETS_BUILD_DIR`.
        """
        output = StringIO()
        today = timezone.localdate().strftime("%Y%m%d")
        datasets_dir = Path(gettempdir()).joinpath("ts_api_test_datasets")
        datasets_dir.mkdir()

        for num in range(10):
            datasets_dir.joinpath(f"{self.dataset_base_name}{num}").write_text("test")

        datasets = list(datasets_dir.iterdir())
        self.assertEqual(len(datasets), 10)

        call_command("create_dataset", keep_only=4, stdout=output)
        archive_path = datasets_dir.joinpath(f"{self.dataset_base_name}{today}")
        output_str = output.getvalue()

        # The new dataset should have been created.
        self.assertTrue(archive_path.exists())

        # 10 datasets should have been kept by default
        datasets = list(datasets_dir.iterdir())
        self.assertEqual(len(datasets), 4)

        # The deleted archives should appear in the logs.
        self.assertEqual(output_str.count("deleted old"), 7)
        self.assertIn("success", output_str)

    def test_cmd_keep_all_option(self):
        """
        With the --keep-all option, the `create_dataset` command should not
        remove any file in the `DATASETS_BUILD_DIR`.
        """
        output = StringIO()
        today = timezone.localdate().strftime("%Y%m%d")
        datasets_dir = Path(gettempdir()).joinpath("ts_api_test_datasets")
        datasets_dir.mkdir()

        for num in range(20):
            datasets_dir.joinpath(f"{self.dataset_base_name}{num}").write_text("plip")

        datasets = list(datasets_dir.iterdir())
        self.assertEqual(len(datasets), 20)

        call_command("create_dataset", keep_all=True, stdout=output)
        archive_path = datasets_dir.joinpath(f"{self.dataset_base_name}{today}")
        output_str = output.getvalue()

        # The new dataset should have been created.
        self.assertTrue(archive_path.exists())

        # 10 datasets should have been kept by default
        datasets = list(datasets_dir.iterdir())
        self.assertEqual(len(datasets), 21)

        # The option --keep-all should appear in the logs.
        self.assertIn("the option --keep-all is set, old datasets won't be deleted", output_str)
        self.assertIn("success", output_str)
