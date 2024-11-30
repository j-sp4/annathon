from loguru import logger
import traceback
import requests
import json
import re
import os

class ErrorLogger:
    def __init__(self, notify="ALL"):
        self.container = "analysis-backend"
        self.notify = notify

    def escape_slack_formatting(self, unescaped_message):
        escaped_message = re.sub(r'&', '&amp;', unescaped_message)
        escaped_message = re.sub(r'<', '&lt;', escaped_message)
        escaped_message = re.sub(r'>', '&gt;', escaped_message)
        escaped_message = re.sub(r'\*', '\\*', escaped_message)
        # escaped_message = re.sub(r'_', '\\_', escaped_message)
        escaped_message = re.sub(r'~', '\\~', escaped_message)
        escaped_message = re.sub(r'`', '\\`', escaped_message)
        return escaped_message

    def make_json_post_request(self, url, data):
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.content

    def write(self, message):

        # output Error details to console
        # print(message)

        try:
            js = json.loads(message)

            # critical error
            if(js['record']['level']['no'] >= 40):
  
                # print traceback to console
                traceback.print_exc()

                # send to slack
                if self.notify == "ALL":

                    line_number = js["record"]["line"]
                    traceback_log = traceback.format_exc()

                    # Extract line number from traceback log
                    tb_lines = traceback_log.split("\n")
                    for line in tb_lines:
                        if line.startswith("  File"):
                            line_number = line.split(",")[1].strip().replace("line ", "")
                            break

                    slack_msg = (f'''🛑 *Failure in {self.container}* \n{self.escape_slack_formatting(js["record"]["message"])}\n\n*Line {line_number}*\n{js["record"]["file"]["path"]}\n\n*Traceback*\n```{self.escape_slack_formatting(traceback.format_exc())}```''') # {js['record']['level']['icon']} {js['record']['level']['name']}
                
                    # bot channel
                    self.make_json_post_request(str(os.getenv("SLACK_FAIL_BOT_WEBHOOK_URL")), {"text": slack_msg})
        except:
            print(message)
            traceback.print_exc()
            print("Error parsing ErrorLogger response")

logger.add(ErrorLogger(notify=str(os.getenv("SLACK_FAIL_BOT_NOTIFY"))), serialize=True)

# example usage
# logger.trace("Executing program")
# logger.debug("Processing data...")
# logger.info("Server started successfully.")
# logger.success("Data processing completed successfully.")
# logger.warning("Invalid configuration detected.")
# logger.error("Failed to connect to the database.")
# logger.critical("Unexpected system error occurred. Shutting down.")