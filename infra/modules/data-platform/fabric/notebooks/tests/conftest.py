import sys
from pathlib import Path

import pytest
from pyspark.sql import SparkSession

# Make `_lib` importable the same way the Fabric notebook imports it.
_NOTEBOOK_DIR = Path(__file__).resolve().parent.parent
if str(_NOTEBOOK_DIR) not in sys.path:
    sys.path.insert(0, str(_NOTEBOOK_DIR))


@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder.master("local[2]")
        .appName("sprint08-notebook-tests")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.driver.memory", "512m")
        .getOrCreate()
    )
