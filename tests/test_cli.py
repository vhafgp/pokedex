from typer.testing import CliRunner

from pokedex.cli import app
from pokedex.models import Pokemon
from pokedex.snapshot import build_snapshot

runner = CliRunner()


def _build_db(tmp_path):
    db = tmp_path / "dex.sqlite"
    build_snapshot(
        db,
        [
            Pokemon(
                id=7, name="squirtle", height=5, weight=90,
                types=("water",), abilities=("torrent",), stats={"hp": 44},
            ),
            Pokemon(
                id=25, name="pikachu", height=4, weight=60,
                types=("electric",), abilities=("static",), stats={"hp": 35},
            ),
        ],
    )
    return db


def test_cli_get(tmp_path):
    db = _build_db(tmp_path)
    result = runner.invoke(app, ["get", "pikachu", "--db", str(db)])
    assert result.exit_code == 0
    assert "#25 pikachu" in result.stdout
    assert "electric" in result.stdout


def test_cli_get_missing_exits_nonzero(tmp_path):
    db = _build_db(tmp_path)
    result = runner.invoke(app, ["get", "missingno", "--db", str(db)])
    assert result.exit_code == 1


def test_cli_search_by_type(tmp_path):
    db = _build_db(tmp_path)
    result = runner.invoke(app, ["search", "--type", "water", "--db", str(db)])
    assert result.exit_code == 0
    assert "#7 squirtle" in result.stdout
    assert "pikachu" not in result.stdout
