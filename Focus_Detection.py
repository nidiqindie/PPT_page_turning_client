import win32gui
import win32process
import psutil
import time
import multiprocessing
from multiprocessing import Process, Queue
import threading

class Focus_Detection():
    """
    焦点检测类，用于监测和获取当前焦点窗口的信息。

    该类提供了启动和停止焦点监测进程的功能，并能够获取当前活动窗口的信息。
    核心功能包括：
    - 启动后台监测进程（start_monitoring）
    - 停止后台监测进程（stop_monitoring）
    - 获取当前活动窗口信息（get_active_window_info）
    - 获取当前焦点信息（get_current_focus_info）
    - 检查监测进程是否活跃（is_monitoring_active）
    - 设置中断回调函数（set_interrupt_callback）
    - 添加/移除中断目标进程（add_interrupt_target/remove_interrupt_target）

    使用示例：
    monitor = Focus_Detection()
    
    # 设置中断回调函数
    monitor.set_interrupt_callback(interrupt_callback)
    
    # 添加需要监听的目标进程（PowerPoint）
    monitor.add_interrupt_target("POWERPNT.EXE")  # PowerPoint
    # 可以添加更多目标进程
    # monitor.add_interrupt_target("notepad.exe")  # 记事本
    # monitor.add_interrupt_target("chrome.exe")   # Chrome浏览器
    其中：
    interrupt_callback用于设置当焦点切换到指定进程时触发的回调函数。
    构造函数参数：
    无

    特殊使用限制或潜在的副作用：
    - 该类依赖于 `psutil`、`win32gui` 和 `win32process` 库，确保在使用前已安装。
    - 监测进程为守护进程，程序退出时监测进程会自动终止。
    - 获取窗口信息时可能会受到系统权限的限制。
    """
    
    def __init__(self):
        self.info_queue = Queue()  # 创建一个队列，用于存储焦点窗口信息
        self.interrupt_queue = Queue()  # 创建一个队列，用于存储中断事件
        self.monitor_process = None  # 创建一个进程变量，用于存储监测进程
        self.latest_info = None  # 创建一个变量，用于存储最新焦点窗口信息
        self.running = False  # 创建一个变量，用于存储监测进程是否正在运行
        self.interrupt_targets = set()  # 存储需要监听中断的目标进程名
        self.interrupt_callback = None  # 中断回调函数
        self.interrupt_thread = None  # 中断处理线程
        self.interrupt_thread_running = False  # 中断线程运行状态
    
    def set_interrupt_callback(self, callback_function):
        """设置中断回调函数
        
        Args:
            callback_function: 回调函数，接收参数(event_type, process_name, window_info)
                             event_type: 'enter' 或 'exit'
                             process_name: 进程名
                             window_info: 窗口信息字典
        """
        self.interrupt_callback = callback_function
    
    def add_interrupt_target(self, process_name):
        """添加需要监听中断的目标进程名
        
        Args:
            process_name: 进程名，如 'POWERPNT.EXE'
        """
        self.interrupt_targets.add(process_name.upper())
    
    def remove_interrupt_target(self, process_name):
        """移除中断目标进程名
        
        Args:
            process_name: 进程名
        """
        self.interrupt_targets.discard(process_name.upper())
    
    @staticmethod
    def _monitor_worker(queue, interrupt_queue, interrupt_targets):
        """子进程工作函数，持续监测焦点窗口"""
        detector = Focus_Detection()
        previous_process = None
        
        while True:
            try:
                window_info = detector.get_active_window_info()
                if window_info:
                    current_process = window_info['process_name'].upper()
                    
                    # 检查是否需要触发中断事件
                    if interrupt_targets:
                        # 检查是否进入目标进程
                        if current_process in interrupt_targets and (previous_process is None or previous_process not in interrupt_targets):
                            interrupt_event = {
                                'event_type': 'enter',
                                'process_name': window_info['process_name'],
                                'window_info': window_info,
                                'timestamp': time.time()
                            }
                            interrupt_queue.put(interrupt_event)
                        
                        # 检查是否离开目标进程
                        elif previous_process is not None and previous_process in interrupt_targets and current_process not in interrupt_targets:
                            interrupt_event = {
                                'event_type': 'exit',
                                'process_name': previous_process,
                                'window_info': window_info,
                                'timestamp': time.time()
                            }
                            interrupt_queue.put(interrupt_event)
                    
                    previous_process = current_process
                    
                    # 将最新信息放入队列，如果队列满了就丢弃旧信息
                    if not queue.empty():
                        try:
                            queue.get_nowait()  # 移除旧信息
                        except:
                            pass
                    queue.put(window_info)
                
                time.sleep(0.5)  # 每0.5秒检测一次
            except Exception as e:
                print(f"监测进程错误: {e}")
                time.sleep(1)
    
    def _interrupt_handler(self):
        """中断事件处理线程"""
        while self.interrupt_thread_running:
            try:
                if not self.interrupt_queue.empty():
                    interrupt_event = self.interrupt_queue.get_nowait()
                    if self.interrupt_callback:
                        self.interrupt_callback(
                            interrupt_event['event_type'],
                            interrupt_event['process_name'],
                            interrupt_event['window_info']
                        )
                time.sleep(0.1)  # 快速检查中断事件
            except Exception as e:
                print(f"中断处理错误: {e}")
                time.sleep(0.5)
    
    def start_monitoring(self):
        """启动后台监测进程"""
        if self.monitor_process is None or not self.monitor_process.is_alive():
            # 启动监测进程，传递中断目标列表
            self.monitor_process = Process(
                target=self._monitor_worker, 
                args=(self.info_queue, self.interrupt_queue, self.interrupt_targets)
            )
            self.monitor_process.daemon = True  # 设置为守护进程
            self.monitor_process.start()
            self.running = True
            
            # 启动中断处理线程
            if self.interrupt_callback and not self.interrupt_thread_running:
                self.interrupt_thread_running = True
                self.interrupt_thread = threading.Thread(target=self._interrupt_handler)
                self.interrupt_thread.daemon = True
                self.interrupt_thread.start()
            
            print("焦点监测进程已启动")
    

    
    def get_active_window_info(self):
        """获取当前活动窗口信息"""
        try:
            # 获取前台窗口句柄
            hwnd = win32gui.GetForegroundWindow()

            # 获取窗口标题
            window_title = win32gui.GetWindowText(hwnd)

            # 获取窗口类名
            class_name = win32gui.GetClassName(hwnd)

            # 获取进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # 获取进程名
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except:
                process_name = "Unknown"

            return {
                'window_handle': hwnd,
                'window_title': window_title,
                'class_name': class_name,
                'process_id': pid,
                'process_name': process_name
            }
        except Exception as e:
            return None
    
    def get_current_focus_info(self):
        """获取当前焦点信息（从子进程获取最新数据）"""
        try:
            # 尝试从队列中获取最新信息
            while not self.info_queue.empty():
                self.latest_info = self.info_queue.get_nowait()
            return self.latest_info
        except:
            return self.latest_info
    
    def is_monitoring_active(self):
        """检查监测进程是否活跃"""
        return self.monitor_process and self.monitor_process.is_alive()
    def stop_monitoring(self):
        """停止监控进程"""
        if hasattr(self, 'monitor_process') and self.monitor_process:
            if self.monitor_process.is_alive():
                self.monitor_process.terminate()  # 终止进程
                self.monitor_process.join(timeout=2)  # 等待进程结束
                if self.monitor_process.is_alive():
                    self.monitor_process.kill()  # 强制结束
    def __del__(self):
        """析构函数，确保在对象销毁时正确清理所有资源"""
        try:
            # 停止中断处理线程
            if hasattr(self, 'interrupt_thread_running'):
                self.interrupt_thread_running = False
            
            if hasattr(self, 'interrupt_thread') and self.interrupt_thread:
                if self.interrupt_thread.is_alive():
                    self.interrupt_thread.join(timeout=1)
            
            # 停止监测进程
            if hasattr(self, 'monitor_process') and self.monitor_process:
                if self.monitor_process.is_alive():
                    self.monitor_process.terminate()
                    self.monitor_process.join(timeout=2)
                    if self.monitor_process.is_alive():
                        self.monitor_process.kill()
            
            # 清理队列资源
            if hasattr(self, 'info_queue') and self.info_queue:
                try:
                    while not self.info_queue.empty():
                        self.info_queue.get_nowait()
                except:
                    pass
                
            if hasattr(self, 'interrupt_queue') and self.interrupt_queue:
                try:
                    while not self.interrupt_queue.empty():
                        self.interrupt_queue.get_nowait()
                except:
                    pass
                
            # 重置状态标志
            if hasattr(self, 'running'):
                self.running = False
            
            print("Focus_Detection 对象已销毁，所有资源已清理")
            
        except Exception as e:
            # 在析构函数中避免抛出异常
            print(f"销毁 Focus_Detection 对象时出错: {e}")


if __name__ == "__main__":
    # 示例回调函数
    def interrupt_callback(event_type, process_name, window_info):
        """中断事件回调函数示例"""
        if event_type == 'enter':
            print(f"🔴 中断触发：进入 {process_name} - {window_info['window_title']}")
        elif event_type == 'exit':
            print(f"🟢 中断触发：离开 {process_name}")
    print("监控器调试")    
    monitor = Focus_Detection()
    
    # 设置中断回调函数
    monitor.set_interrupt_callback(interrupt_callback)
    
    # 添加需要监听的目标进程（PowerPoint）
    monitor.add_interrupt_target("POWERPNT.EXE")  # PowerPoint
    # 可以添加更多目标进程
    # monitor.add_interrupt_target("notepad.exe")  # 记事本
    # monitor.add_interrupt_target("chrome.exe")   # Chrome浏览器
    
    monitor.start_monitoring()
    
    try:
        while True:
            current_info = monitor.get_current_focus_info()
            if current_info:
                print(f"当前焦点：{current_info['process_name']} - {current_info['window_title']}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n正在停止监控...")
        monitor.stop_monitoring()
