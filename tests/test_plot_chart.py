"""Test the plot_chart tool in app.tools."""
import sys, os, shutil
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for tests

# Ensure app package importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.tools import plot_chart

def test_plot_chart(tmp_path):
    # Copy example CSV to temporary path
    src = os.path.join(os.path.dirname(__file__), '..', 'examples', 'iris.csv')
    dest = tmp_path / 'iris.csv'
    shutil.copy(src, dest)
    # Define code to plot a histogram of sepal_length
    code = (
        'import pandas as pd\n'
        'import matplotlib.pyplot as plt\n'
        'df = pd.read_csv(csv_path)\n'
        "df['sepal_length'].hist()"
    )
    files = plot_chart(code, str(dest))
    assert isinstance(files, list)
    assert len(files) == 1
    img_path = files[0]
    assert os.path.exists(img_path)
    # File should be non-empty PNG
    assert img_path.lower().endswith('.png')
    assert os.path.getsize(img_path) > 0