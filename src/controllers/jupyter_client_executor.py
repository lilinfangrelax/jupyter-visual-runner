from jupyter_client import KernelManager
from queue import Empty

class JupyterClientExecutor:
    def __init__(self, kernel_name):
        self.kernel_manager = KernelManager(kernel_name=kernel_name)
        self.kernel_manager.start_kernel()
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()
        self.kernel_client.wait_for_ready()

    def execute(self, code):
        msg_id = self.kernel_client.execute(code)
        print(msg_id)
        while True:
            try:
                msg = self.kernel_client.get_iopub_msg(timeout=1)
                print(f" {code.split('\n')[0]}: {msg}")
                content = msg["content"]
                if msg["msg_type"] == "stream" and content["name"] == "stdout":
                    print("stream")
                    break
                elif msg["msg_type"] == "error":
                    print("error")
                    break
                elif msg["msg_type"] == "status":
                    if content["execution_state"] == "idle" and msg_id == msg["parent_header"]["msg_id"]:
                        print("idle")
                        break
            except KeyboardInterrupt:
                print("Interrupted by user.")
                break
            except Empty:
                # If no messages are available, we'll end up here, but we can just continue and try again.
                pass

    def shutdown(self):
        '''
            Don't know why, but I should use it: Shut down the kernel and the client.
            https://github.com/jupyter/jupyter_client/issues/1026#issuecomment-2726203528
        '''
        if self.kernel_client:
            self.kernel_client.stop_channels()
            self.kernel_client = None
        if self.kernel_manager:
            self.kernel_manager.shutdown_kernel()
            self.kernel_manager = None

if __name__ == "__main__":
    jupyter_client_executor = JupyterClientExecutor("python3")
    jupyter_client_executor.execute("print('Hello, World')")
