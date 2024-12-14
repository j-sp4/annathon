import tempfile
import pytest
from benchmarking.benchmarker import Benchmarker

@pytest.fixture
def benchmarker():

    """
    TODO:
    """

    benchmarker = Benchmarker()

    return benchmarker

def test_benchmarker_init(benchmarker):
    """
    TODO:
    """

    assert benchmarker.filepath_results == "benchmark_results.txt"
    assert benchmarker.dir_benchmarking == "./benchmarking"
    assert benchmarker.dir_working == None
