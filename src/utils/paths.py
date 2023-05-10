from contextlib import contextmanager
from pathlib import Path
import pathlib
import os
import sys
import re
import platform
from rich.console import Console
console=Console()
import arrow

from ..constants import configPath,DIR_FORMAT_DEFAULT,DATE_DEFAULT,SAVE_LOCATION_DEFAULT
from ..utils import profiles
import src.utils.config as config_


homeDir=pathlib.Path.home()
config = config_.read_config()['config']
@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

        Args:``
            path (``Path): The path to the cwd

    Yields:
        None
    """


    origin = Path().absolute()
    createDir(Path(str(path)))
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)
def createDir(path):
    try:
        path.mkdir(exist_ok=True,parents=True)
    except:
        console.print("Error creating directory, check the directory and make sure correct permissions have been issued.")
        sys.exit()
def databasePathHelper(model_id,username):
    return pathlib.Path(config.get("metadata").format(configpath=homeDir / configPath,profile=profiles.get_current_profile(),model_username=username,username=username,model_id=model_id,sitename="Onlyfans",site_name="Onlyfans",first_letter=username[0]),"user_data.db")

def getmediadir(ele,username,model_id):
    root= pathlib.Path((config.get('save_location') or SAVE_LOCATION_DEFAULT))
    downloadDir=(config.get('dir_format') or DIR_FORMAT_DEFAULT ).format(sitename="onlyfans",first_letter=username[0].capitalize(),model_id=model_id,model_username=username,responsetype=ele.responsetype.capitalize(),mediatype=ele.mediatype.capitalize(),value=ele.value.capitalize(),date=arrow.get(ele.postdate).format(config.get('date') or DATE_DEFAULT))
    return root /downloadDir   


def messageResponsePathHelper(model_id,username):
    profile = profiles.get_current_profile()
    return homeDir / configPath / profile / ".data"/f"{username}_{model_id}"/"messages.json"


def timelineResponsePathHelper(model_id,username):
    profile = profiles.get_current_profile()
    return homeDir / configPath / profile / ".data"/f"{username}_{model_id}"/"timeline.json"


def archiveResponsePathHelper(model_id,username):
    profile = profiles.get_current_profile()
    return homeDir / configPath / profile / ".data"/f"{username}_{model_id}"/"archive.json"
def pinnedResponsePathHelper(model_id,username):
    profile = profiles.get_current_profile()
    return homeDir / configPath / profile / ".data"/f"{username}_{model_id}"/"pinned.json"

def cleanup():
    console.print("Cleaning up .part files\n\n")
    root= pathlib.Path((config.get('save_location') or SAVE_LOCATION_DEFAULT))
    for file in list(filter(lambda x:re.search("\.part$",str(x))!=None,root.glob("**/*"))):
        file.unlink(missing_ok=True)


def getlogpath():
    path=pathlib.Path.home() / configPath / "logging"/f'ofscraper_{config_.get_main_profile()}_{arrow.get().format("YYYY-MM-DD")}.log'
    createDir(path.parent)
    return path
def get_mp4tool():
    if platform.system == 'Windows':
        return pathlib.Path(__file__).parents[2] /"bin"/"mp4decrypt.exe"
    else:
        return pathlib.Path(__file__).parents[2] /"bin"/"mp4decrypt"

def getcachepath():
    profile = profiles.get_current_profile()
    path=pathlib.Path.home() / configPath / profile
    createDir(path.parent)
    return path
def trunicate(path):
    if platform.system() == 'Windows' and len(str(path))>256:
        return _windows_trunicateHelper(path)
    elif platform.system() == 'Linux':
        return _linux_trunicateHelper(path)
    else:
        return pathlib.Path(path)
def _windows_trunicateHelper(path):
    path=pathlib.Path(path)
    if re.search("\.[a-z]*$",path.name,re.IGNORECASE):
        ext=re.search("\.[a-z]*$",path.name,re.IGNORECASE).group(0)
    else:
        ext=""
    filebase=str(path.with_suffix("").name)
    dir=path.parent
    #-1 for path split /
    maxLength=256-len(ext)-len(str(dir))-1
    outString=""
    for ele in list(filebase):
        temp=outString+ele
        if len(temp)>maxLength:
            break
        outString=temp
    return pathlib.Path(f"{pathlib.Path(dir,outString)}{ext}")

def _linux_trunicateHelper(path):
    path=pathlib.Path(path)
    if re.search("\.[a-z]*$",path.name,re.IGNORECASE):
        ext=re.search("\.[a-z]*$",path.name,re.IGNORECASE).group(0)
    else:
        ext=""
    filebase=str(re.sub(ext,"",path.name))
    dir=path.parent
    maxLength=255-len(ext.encode('utf8'))
    outString=""
    for ele in list(filebase):
        temp=outString+ele
        if len(temp.encode("utf8"))>maxLength:
            break
        outString=temp
    return pathlib.Path(f"{pathlib.Path(dir,outString)}{ext}")
