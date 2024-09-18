import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# there isnt always a pot of gold at the end of the rainbow :sob:, sometimes god gives you gold, sometimes inheriently messy classes
class ConsoleColors:
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'white': '\033[97m',
        'light_grey': '\033[37m',
        'grey': '\033[90m',
        'brown': '\033[38;5;94m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'light_red': '\033[91m',
        'dark_green': '\033[32m',
        'dark_red': '\033[31m',
        'light_cyan': '\033[96m',
        'light_green': '\033[92m',
        'endc': '\033[0m'
    }

    @classmethod
    def get(cls, color_name):
        return cls.colors.get(color_name, cls.colors['endc'])

# class for handling color mapping
class LogColorMapper:
    color_map = {
        'FLog::Network': 'green',
        'FLog::Error': 'red',
        'FLog::Warning': 'yellow',
        'FLog::Output': 'light_grey',
        'FLog::Audio': 'brown',
        'FLog::LogWin32BTId': 'magenta',
        'FLog::Graphics': 'cyan',
        'FLog::WindowsLuaApp': 'blue',
        'FLog::CrashReportLog': 'light_red',
        'FLog::SingleSurfaceApp': 'dark_green',
        'FLog::DataModelPatchConfigurer': 'light_cyan',
        'FLog::GameJoinUtil': 'light_green',
        'FLog::UGCGameController': 'magenta',
        'DFLog::FriendServiceLocalRequests': 'green',
        'DFLog::MegaReplicatorLogDisconnectCleanUpLog': 'dark_red',
        'DFLog::HttpTraceError': 'dark_green'
    }

    @classmethod
    def get_color(cls, log_line):
        for key, color in cls.color_map.items():
            if key in log_line:
                return ConsoleColors.get(color)
        return ConsoleColors.get('blue')

# get log file #######
LOG_PATH = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Roblox', 'logs')

class LogFileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.latest_file = None
        self.file_position = 0
        self.update_latest_file()
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.latest_file:
            self.process_file(event.src_path)
    
    def update_latest_file(self):
        new_latest_file = get_latest_log_file(LOG_PATH)
        if new_latest_file and new_latest_file != self.latest_file:
            self.latest_file = new_latest_file
            self.file_position = 0  # reset pos
            print(f"{ConsoleColors.get('green')}[-] found new log file: {os.path.basename(self.latest_file)} ({time.ctime(os.path.getctime(self.latest_file))}){ConsoleColors.get('endc')}")
    
    def process_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as log_file: #roblox is fucking weird
                log_file.seek(self.file_position)
                for line in log_file:
                    if 'FLog' in line or 'DFLog' in line:
                        print(format_log_line(line))
                self.file_position = log_file.tell()
        except IOError:
            print(f"{ConsoleColors.get('red')}unable to open {file_path}{ConsoleColors.get('endc')}")
        except Exception as e:
            print(f"{ConsoleColors.get('red')}error processing {e}{ConsoleColors.get('endc')}")

def get_latest_log_file(log_path):
    try:
        log_files = [
            os.path.join(log_path, file)
            for file in os.listdir(log_path)
            if os.path.isfile(os.path.join(log_path, file))
        ]
        if not log_files:
            print(f"{ConsoleColors.get('red')}no log file(s) found{ConsoleColors.get('endc')}")
            return None
        return max(log_files, key=os.path.getctime)
    except Exception as e:
        print(f"{ConsoleColors.get('red')}error accessing {e}{ConsoleColors.get('endc')}")
        return None

def format_log_line(line):
    start_index = line.find('[')
    end_index = line.find(']')
    if start_index == -1 or end_index == -1:
        return line
    
    inside_brackets = line[start_index:end_index+1]
    color = LogColorMapper.get_color(line)
    outside_text = line[end_index+1:].strip()

    if 'FLog::Output' in line: #grey color for output string
        bracket_color = ConsoleColors.get('light_grey')
        return f"{bracket_color}{inside_brackets}{ConsoleColors.get('endc')} {ConsoleColors.get('grey')}{outside_text}{ConsoleColors.get('endc')}"
    
    return f"{color}{inside_brackets}{ConsoleColors.get('endc')} {outside_text}"

def main(): #file monitoring and processing
    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=LOG_PATH, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(0.1)
            event_handler.update_latest_file()
    
    except KeyboardInterrupt:
        print(f"{ConsoleColors.get('red')}bahaha fatty{ConsoleColors.get('endc')}")
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()
