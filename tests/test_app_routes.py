from pathlib import Path
import unittest


class AppRoutesTests(unittest.TestCase):
    def test_main_does_not_register_legacy_tasks_router(self):
        main_source = Path("app/main.py").read_text(encoding="utf-8")

        self.assertNotIn("routes_tasks", main_source)
        self.assertNotIn("tasks_router", main_source)

    def test_board_routes_file_keeps_current_board_endpoints(self):
        board_routes_source = Path("app/board_routes.py").read_text(encoding="utf-8")

        self.assertIn('router = APIRouter(prefix="/board/api"', board_routes_source)
        self.assertIn('"/dates"', board_routes_source)
        self.assertIn('"/days/{date}"', board_routes_source)
        self.assertIn('"/days/{date}/ai-plan"', board_routes_source)
        self.assertIn('"/agent/propose"', board_routes_source)
        self.assertIn('"/agent/execute"', board_routes_source)


if __name__ == "__main__":
    unittest.main()
