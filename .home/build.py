from pathlib import Path
import shutil
source = Path('src')
assert (source / 'index.html').is_file(), 'src/index.html is required'
shutil.copytree(source, 'dist', dirs_exist_ok=True)
assert (Path('dist') / 'index.html').is_file()
print('HOME BUILD PASSED')
