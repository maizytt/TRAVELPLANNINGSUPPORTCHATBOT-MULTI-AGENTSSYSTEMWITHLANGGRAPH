import chainlit as cl
from chainlit import make_async, run_sync
import os 
import asyncio
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
#from workflow import trip_graph
from app_workflow import trip_graph
from recommend_tour_team.agents import general_destination
from state import PlanTripState
from create_tour_team.agents import process_event_choice_chain, process_food_choice_chain, process_places_choice_chain
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open(".env", "r") as f:
    for line in f:
        key, value = line.split("=")
        os.environ[key] = value.strip()

llm = ChatOpenAI(
  model="gpt-4o-mini",
  temperature=0,
  verbose=True
)


# User input
user_inputs = {
    "destination": None,
    "departure": None,
    "travel_time": None,
    "travel_duration": None,
    "budget": None,
    "interests": None
}


# Start the workflow
thread = {"configurable": {"thread_id": "1"}}

state = PlanTripState()
state["recommend_tour_response"] = []
state["tour_choice"] = []
state["chat_query"] = ""
state["recommend_chat"] = ""


workflow_state = {
    "count": -1,
    "step_workflow": -1
}



@cl.on_chat_start
async def start():
    content = (
        "## Xin chào - Tôi là Trip Planner, trợ lý sẽ hỗ trợ bạn xây dựng những chuyến du lịch tuyệt vời!\n\n"
        "Chuyến đi của bạn sẽ có những trải nghiệm thú vị với những địa điểm tham quan, ăn uống nổi bật cùng với những dịch vụ tốt nhất.\n"
        "Cùng bắt đầu với tôi nhé!\n"
        "Trước tiên, tôi cần bạn cung cấp cho tôi những thông tin sau đây:\n"
    )
    await cl.Message(content=content).send()
    await ask_next_question("destination", "Hãy cho tôi biết bạn dự định đi đâu nhé!")

async def ask_next_question(key, question):
    await cl.Message(content=question).send()

# Hàm xử lý các tác vụ không đồng độ 
async def process_workflow(trip_graph,count, step_workflow):
       
    if step_workflow == 0:
        for event in trip_graph.stream(state, thread, stream_mode="values"):
            await asyncio.sleep(120)
            current_state = event
            count += 1
            print(current_state)
            print(current_state.keys())
            print("state", count)

            if count == 2:  # recommend_tour_agent hoặc trip_info_agent
                if 'trip_infor_response' in current_state:

                    return [current_state['trip_infor_response'], 0,0]
                elif 'recommend_tour' in current_state:

                    return [current_state['recommend_tour'], count, step_workflow]
                            
    elif step_workflow == 1:

        for event in trip_graph.stream(None, thread, stream_mode="values"):
            await asyncio.sleep(5)
            current_state = event
            count += 1
            print(current_state)
            print(current_state.keys())
            print("state", count)

            if count == 4:
                if 'accommodation_response' in current_state:
                    return [current_state['accommodation_response'], count, step_workflow]

            if count == 5:  
                if 'completion_tour_response' in current_state:
                    return [current_state['completion_tour_response'], 0, 0]

                elif 'adjust_tour_response' in current_state:
                    return [current_state['adjust_tour_response'], count, step_workflow]
            
            if count == 6:  
                if 'completion_tour_response' in current_state:
                    return [current_state['completion_tour_response'], 0, 0]

    elif step_workflow == 2:
            
        for event in trip_graph.stream(None, thread, stream_mode="values"):
            await asyncio.sleep(30)
            current_state = event
            count += 1
            print(current_state)
            print(current_state.keys())
            print("state", count)
            if count == 6:
                if 'event_response' in current_state:
                    return [current_state['event_response'], count, step_workflow]
            elif count == 7:
                if 'accommodation_response' in current_state:
                    return [current_state['accommodation_response'], count, step_workflow] 
   

    elif step_workflow == 3:
        
        for event in trip_graph.stream(None, thread, stream_mode="values"):
            await asyncio.sleep(180)
            current_state = event
            count += 1
            if count == 8:
                if 'places_response' in current_state:
                    return [current_state['places_response'], count, step_workflow]
            elif count == 9:
                if 'event_response' in current_state:
                    return [current_state['event_response'], count, step_workflow]



    elif step_workflow == 4:

        for event in trip_graph.stream(None, thread, stream_mode="values"):
            await asyncio.sleep(180)
            current_state = event
            count += 1
            if count == 10:
                if 'food_response' in current_state:
                    return [current_state['food_response'], count, step_workflow] 
            elif count == 11:
                if 'places_response' in current_state:
                    return [current_state['places_response'], count, step_workflow] 
    

    elif step_workflow == 5:
        
        for event in trip_graph.stream(None, thread, stream_mode="values"):
          await asyncio.sleep(180)
          current_state = event
          count += 1
          if count == 12:
              if 'transport_response' in current_state:
                  return [current_state['transport_response'], count, step_workflow] 
          elif count == 13:
              if 'food_response' in current_state:
                  return [current_state['food_response'], count, step_workflow] 
      

    elif step_workflow == 6:
    

        for event in trip_graph.stream(None, thread, stream_mode="values"):
            await asyncio.sleep(30)
            current_state = event
            count += 1
            if count == 14:
                if 'generate_tour_response' in current_state:
                    return [current_state['generate_tour_response'], count, step_workflow] 
            if count == 15:
                if 'price_response' in current_state:
                    return [current_state['price_response'], 0, step_workflow] 
                elif 'transport_response' in current_state:
                    return [current_state['transport_response'], count, step_workflow] 
        

    elif step_workflow == 7:
        for event in trip_graph.stream(None, thread, stream_mode="values"):
            await asyncio.sleep(120) 
            current_state = event
            count += 1
            if count == 17:
                if 'generate_tour_response' in current_state:
                    return [current_state['generate_tour_response'], count, step_workflow] 
            if count == 18:
                if 'price_response' in current_state:
                    return [current_state['price_response'], 0, step_workflow] 





@cl.on_message
async def main(message: cl.Message):

    count = workflow_state['count']
    step_workflow = workflow_state['step_workflow']
    print(step_workflow)

    if step_workflow == -1:
        for key in user_inputs:
            if user_inputs[key] is None:
                user_inputs[key] = message.content
                break

        # Xác định câu hỏi tiếp theo
        next_questions = {
            "destination": ("departure", "Bạn sẽ khởi hành từ đâu?"),
            "departure": ("travel_time", "Thời gian bạn bắt đầu đi là khi nào?"),
            "travel_time": ("travel_duration", "Chuyến đi của bạn sẽ kéo dài bao lâu?"),
            "travel_duration": ("budget", "Chi phí bạn dự tính cho chuyến đi là bao nhiêu?"),
            "budget": ("interests", "Bạn có dự định sẽ thăm thú địa điểm cụ thể hay hoạt động nào không?")
        }

        for key, (next_key, question) in next_questions.items():
            if user_inputs[key] is not None and user_inputs[next_key] is None:
                await ask_next_question(next_key, question)
                return

        state['user_inputs'] = user_inputs
        
        info_tour = general_destination(state)

        await cl.Message(content=info_tour).send()



        content = ("Và tôi là **Trip Planner** sẽ hỗ trợ bạn:\n"
        "- #### **Đề xuất gợi ý các tour từ các đại lý du lịch được thiết kế sẵn** \n "
    
        "- #### **Thiết kế tour du lịch theo ý muốn của bạn với những điểm đến bạn muốn đi** \n "

        "- #### **Cung cấp những thông tin cần thiết cho chuyến đi về các điểm tham quan du lịch, các sự kiện lễ hội, món ăn đặc sản, ...** \n "

        "Tôi sẽ hỗ trợ bạn để có chuyến đi tuyệt nhất!")

        await cl.Message(content=content).send()
        workflow_state['step_workflow'] = 0
        
    elif step_workflow == 0:
        human = message.content 
        state['messages'] = HumanMessage(content=human)
        print(state)

        for event in trip_graph.stream(state, thread, stream_mode="values"):
            current_state = event
            count += 1
            print(current_state)
            print(current_state.keys())
            print("state", count)

            if count == 2:  # recommend_tour_agent hoặc trip_info_agent
                if 'trip_infor_response' in current_state:
                    await cl.Message(content= current_state['trip_infor_response']).send()
                    workflow_state['step_workflow'] = 0
                    count = 0
                elif 'recommend_tour' in current_state:
                    await cl.Message(content=current_state['recommend_tour']).send() 

        print(count)
        if count == 2:
            content = ("\n ## **Bây giờ chúng tôi sẽ hỗ trợ bạn tạo một tour theo với các hoạt động trải nghiệm ý muốn của bạn nhé!** \n"
            "Chúng tôi sẽ đề xuất lần lượt cho bạn các thông tin về thời tiết, sự kiện, nơi lưu trú, các địa điểm tham quan, các món ăn/ đồ uống ngon và các hình thức di chuyển.\n"
            "Tiếp theo, bạn hãy trả lời cho tôi biết những danh sách địa điểm, sự kiện, món ăn, nơi lưu trú, phương tiện di chuyển, ... để chúng tôi hỗ trợ bạn sắp xếp 1 tour hoàn chỉnh nhất.\n"
            "Lưu ý với mỗi danh sách các sự lọn chọn của bạn hãy cách nhau bằng dấu ',' \n"
            "\nĐầu tiên hãy cho chúng tôi biết cụ thể hơn về loại hình bạn muốn lưu trú (hotel/ homestay/ resort/ ... ), chất lượng số sao mong muốn và giá phòng/ đêm phù hợp với ngân sách của bạn:")
            await cl.Message(content= content).send()
            workflow_state['step_workflow'] = 1
            workflow_state['count'] = count

        elif count == 3:
            content = ("\n Trên đây là các tour phù hợp nhất cho kế hoạch du lịch của bạn. Bạn có cảm thấy hài lòng với những tour đã gợi ý hay không?\n"
            "\t - Nếu có, hãy chọn tour phù hợp với bạn (VD: Tour 1/2).\n "
            "\t - Nếu không, tôi sẽ hỗ trợ bạn xây dựng một tour với những địa điểm tham quan và món ăn nổi bật mà bạn muốn.\n "
            "\t - Nếu bạn muốn chỉnh sửa đôi chút, hãy mô tả chi tiết (địa điểm, thời gian, phương tiện,... cần thay đổi)\n"
            "Hãy nhập vào sự lựa chọn của bạn: ")
            await cl.Message(content= content).send()
            workflow_state['step_workflow'] = 1
            workflow_state['count'] = count

            
       
    elif step_workflow == 1:

        if count == 2:
          human = message.content
          trip_graph.update_state(thread, {"accommodation_query": human})


        elif count == 3:
          human = message.content
          trip_graph.update_state(thread, {"recommend_chat": human})

        for event in trip_graph.stream(None, thread, stream_mode="values"):
            current_state = event
            count += 1
            print(current_state)
            print(current_state.keys())
            print("state", count)

            if count == 4:
                if 'accommodation_response' in current_state:
                    await cl.Message(content=current_state['accommodation_response']).send()

            if count == 5:  
                if 'completion_tour_response' in current_state:
                    await cl.Message(content=current_state['completion_tour_response']).send()
                    workflow_state['step_workflow'] = 0
                    workflow_state['count'] = -1
                    count = 0 

                elif 'adjust_tour_response' in current_state:
                    await cl.Message(content=current_state['adjust_tour_response']).send()
            
            if count == 6:  
                if 'completion_tour_response' in current_state:
                    await cl.Message(content=current_state['completion_tour_response']).send()
                    workflow_state['step_workflow'] = 0
                    workflow_state['count'] = -1
                    count = 0 

        print(count)
        if count == 4:
            await cl.Message(content= "Hãy nhập vào tên địa điểm bạn muốn lưu trú: ").send()
            workflow_state['step_workflow'] = 2 
            workflow_state['count'] = count

        elif count == 5:
            content = ("\n ## **Bây giờ chúng tôi sẽ hỗ trợ bạn tạo một tour theo với các hoạt động trải nghiệm ý muốn của bạn nhé!** \n"
            "Chúng tôi sẽ đề xuất lần lượt cho bạn các thông tin về thời tiết, sự kiện, nơi lưu trú, các địa điểm tham quan, các món ăn/ đồ uống ngon và các hình thức di chuyển.\n"
            "Tiếp theo, bạn hãy trả lời cho tôi biết những danh sách địa điểm, sự kiện, món ăn, nơi lưu trú, phương tiện di chuyển, ... để chúng tôi hỗ trợ bạn sắp xếp 1 tour hoàn chỉnh nhất."
            "Lưu ý với mỗi danh sách các sự lọn chọn của bạn hãy cách nhau bằng dấu ',' \n"
            "\nĐầu tiên hãy cho chúng tôi biết cụ thể hơn về loại hình bạn muốn lưu trú (hotel/ homestay/ resort/ ... ), chất lượng số sao mong muốn và giá phòng/ đêm phù hợp với ngân sách của bạn:")
            await cl.Message(content= content).send()
            workflow_state['step_workflow'] = 2 
            workflow_state['count'] = count


    elif step_workflow == 2:

        if count == 4:
            human = message.content
            trip_graph.update_state(thread, {"user_accommodation_choice": human})

        elif count == 5:
            human = message.content
            trip_graph.update_state(thread, {"accommodation_query": human})
            
        result = run_sync(process_workflow(trip_graph, count, step_workflow))
        print(result)
        content = result[0]
        await cl.Message(content= content).send()

        count = result[1]
        workflow_state['step_workflow'] = result[2]
        if count == 0:
            workflow_state['count'] = -1
        
        if count == 6:
            await cl.Message(content= "Hãy nhập vào tên sự kiện bạn muốn tham quan: ").send()
            workflow_state['step_workflow'] = 3 
            workflow_state['count'] = count
        elif count == 7:
            await cl.Message(content= "Hãy nhập vào tên địa điểm bạn muốn lưu trú: ").send()
            workflow_state['step_workflow'] = 3
            workflow_state['count'] = count

        

    elif step_workflow == 3:
        if count == 6:
            human = message.content
            human = process_event_choice_chain.invoke({"input": human})
            trip_graph.update_state(thread, {"user_event_choice": human})

        elif count == 7:
            human = message.content
            trip_graph.update_state(thread, {"user_accommodation_choice": human})
        
        result = run_sync(process_workflow(trip_graph, count, step_workflow))
        print(result)
        content = result[0]
        await cl.Message(content= content).send()

        count = result[1]
        workflow_state['step_workflow'] = result[2]
        if count == 0:
            workflow_state['count'] = -1

        if count == 8:
            await cl.Message(content= "Hãy nhập vào tên địa điểm bạn muốn tham quan: ").send()
            workflow_state['step_workflow'] = 4
            workflow_state['count'] = count
        elif count == 9:
            await cl.Message(content= "Hãy nhập vào tên sự kiện bạn muốn tham quan: ").send()
            workflow_state['step_workflow'] = 4
            workflow_state['count'] = count



    elif step_workflow == 4:
        if count == 8:
            human = message.content
            human = process_places_choice_chain.invoke({"input": human})
            trip_graph.update_state(thread, {"user_places_choice": human})

        elif count == 9:
            human = message.content
            human = process_event_choice_chain.invoke({"input": human})
            trip_graph.update_state(thread, {"user_event_choice": human})

        result = run_sync(process_workflow(trip_graph, count, step_workflow))
        print(result)
        content = result[0]
        await cl.Message(content= content).send()

        count = result[1]
        workflow_state['step_workflow'] = result[2]
        if count == 0:
            workflow_state['count'] = -1

        if count == 10:
            await cl.Message(content= "Hãy nhập vào tên món ăn/ đồ uống bạn muốn thưởng thức: ").send()
            workflow_state['step_workflow'] = 5
            workflow_state['count'] = count
        elif count == 11:
            await cl.Message(content= "Hãy nhập vào tên địa điểm bạn muốn tham quan: ").send()
            workflow_state['step_workflow'] = 5 
            workflow_state['count'] = count
    

    elif step_workflow == 5:
        if count == 10:
            human = message.content
            human = process_food_choice_chain.invoke({"input": human})
            trip_graph.update_state(thread, {"user_food_choice": human})
        elif count == 11:
            human = message.content
            human = process_places_choice_chain.invoke({"input": human})
            trip_graph.update_state(thread, {"user_places_choice": human})
        
        result = run_sync(process_workflow(trip_graph, count, step_workflow))
        print(result)
        content = result[0]
        await cl.Message(content= content).send()

        count = result[1]
        workflow_state['step_workflow'] = result[2]
        if count == 0:
            workflow_state['count'] = -1

        if count == 12:
            await cl.Message(content= "Hãy nhập vào phương tiện di chuyển bạn muốn đi: ").send()
            workflow_state['step_workflow'] = 6 
            workflow_state['count'] = count

        elif count == 13:
            await cl.Message(content= "Hãy nhập vào tên món ăn/ đồ uống bạn muốn thưởng thức: ").send()
            workflow_state['step_workflow'] = 6 
            workflow_state['count'] = count

    elif step_workflow == 6:
      
        if count == 12:
            human = message.content
            trip_graph.update_state(thread, {"user_transport_choice": human})

        elif count == 13:
            human = message.content
            human = process_food_choice_chain.invoke({"input": human})
            trip_graph.update_state(thread, {"user_food_choice": human})

        for event in trip_graph.stream(None, thread, stream_mode="values"):
            current_state = event
            count += 1
            if count == 14:
                if 'generate_tour_response' in current_state:
                    await cl.Message(content=current_state['generate_tour_response']).send()
            if count == 15:
                if 'price_response' in current_state:
                    await cl.Message(content=current_state['price_response']).send()
                    workflow_state['step_workflow'] = 0
                    workflow_state['count'] = -1
                    count = 0 
                elif 'transport_response' in current_state:
                    await cl.Message(content=current_state['transport_response']).send()
        if count ==15:
            await cl.Message(content= "Hãy nhập vào phương tiện di chuyển bạn muốn đi: ").send()
            workflow_state['step_workflow'] = 7
            workflow_state['count'] = count
        

    elif step_workflow == 7:
        if count ==15:
            human = message.content
            trip_graph.update_state(thread, {"user_transport_choice": human})
        for event in trip_graph.stream(None, thread, stream_mode="values"):
            current_state = event
            count += 1
            if count == 17:
                if 'generate_tour_response' in current_state:
                    await cl.Message(content=current_state['generate_tour_response']).send()
            if count == 18:
                if 'price_response' in current_state:
                    await cl.Message(content=current_state['price_response']).send()
                    workflow_state['step_workflow'] = 0
                    workflow_state['count'] = -1
                    count = 0 
