from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

instruction_path = f"{os.getenv('APP_ROOT')}/{os.getenv('INSTRUCTIONS_FILE')}"

def get_instructions(file_path=instruction_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            instructions = file.read()
        return instructions
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred while reading the file:", e)


# def get_current_status():
#     orderbook = pyupbit.get_orderbook(ticker="KRW-BTC")
#     current_time = orderbook['timestamp']
#     btc_balance = 0
#     krw_balance = 0
#     btc_avg_buy_price = 0
#     balances = upbit.get_balances()
#     for b in balances:
#         if b['currency'] == "BTC":
#             btc_balance = b['balance']
#             btc_avg_buy_price = b['avg_buy_price']
#         if b['currency'] == "KRW":
#             krw_balance = b['balance']

#     current_status = {'current_time': current_time, 'orderbook': orderbook, 'btc_balance': btc_balance, 'krw_balance': krw_balance, 'btc_avg_buy_price': btc_avg_buy_price}
#     return json.dumps(current_status)


# def analyze_data_with_gpt4(data_json):
#     instructions_path = "instructions.md"
#     try:
#         instructions = get_instructions(instructions_path)
#         if not instructions:
#             print("No instructions found.")
#             return None

#         current_status = get_current_status()
#         response = client.chat.completions.create(
#             model="gpt-4-turbo-preview",
#             messages=[
#                 {"role": "system", "content": instructions},
#                 {"role": "user", "content": data_json},
#                 {"role": "user", "content": current_status}
#             ],
#             response_format={"type":"json_object"}
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"Error in analyzing data with GPT-4: {e}")
#         return None

if __name__ == "__main__":
    print(instruction_path)
    print(get_instructions())