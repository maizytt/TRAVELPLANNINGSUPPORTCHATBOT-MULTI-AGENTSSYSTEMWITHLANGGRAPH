from langchain_core.messages import HumanMessage
from workflow import trip_graph
from state import PlanTripState
from create_tour_team.agents import process_event_choice_chain, process_food_choice_chain, process_places_choice_chain


user_input = {
    "departure": "Thành phố Hồ Chí Minh",
    "destination": "Đà Lạt",
    "travel_time": "Tháng 2/ 2025",
    "travel_duration": "2 ngày 1 đêm",
    "budget": "4 triệu VND",
    "interests": "Đi ngắm hoa mai anh đào nở"
}

# Start the workflow
thread = {"configurable": {"thread_id": "1"}}
state = PlanTripState()
state["messages"] = HumanMessage(content="Hãy thiết kế tour")
state["user_inputs"] = user_input
state["recommend_tour_response"] = []
state["tour_choice"] = []
state["chat_query"] = ""
state["recommend_chat"] = ""


# Pass an empty dictionary as input to the stream method
count = -1
if count == -1:
  for event in trip_graph.stream(state, thread, stream_mode="values"):
      current_state = event
      count += 1
      print('State', count)
      print(current_state)
      print(current_state.keys())

      if count == 1:  # general_destination
          if 'general_response' in current_state:
              print('Chainlit\n')
              print(current_state['general_response'])

      if count == 2:  # recommend_tour_agent hoặc trip_info_agent
          if 'trip_infor_response' in current_state:
              print('Chainlit\n')
              print(current_state['trip_infor_response'])
              count = -1
          elif 'recommend_tour' in current_state:
              print('Chainlit\n')
              print(current_state['recommend_tour'])

      if count == 3:
          if 'accommodation_response' in current_state:
              print('Chainlit\n')
              print(current_state['accommodation_response'])

#=====================
if count == 2:
    print("\n Bây giờ chúng tôi sẽ hỗ trợ bạn tạo một tour theo với các hoạt động trải nghiệm ý muốn của bạn nhé! \n")
    print("Chúng tôi sẽ đề xuất lần lượt cho bạn các thông tin về thời tiết, sự kiện, nơi lưu trú, các địa điểm tham quan, các món ăn/ đồ uống ngon và các hình thức di chuyển.\n")
    print("Tiếp theo, bạn hãy trả lời cho tôi biết những danh sách địa điểm, sự kiện, món ăn, nơi lưu trú, phương tiện di chuyển, ... để chúng tôi hỗ trợ bạn sắp xếp 1 tour hoàn chỉnh nhất.")
    print("Lưu ý với mỗi danh sách các sự lọn chọn của bạn hãy cách nhau bằng dấu ',' ")
    print("Đầu tiên hãy cho chúng tôi biết cụ thể hơn về loại hình bạn muốn lưu trú (hotel/ homestay/ resort/ ... ), chất lượng số sao mong muốn và giá phòng/ đêm phù hợp với ngân sách của bạn:")
    human = input("Nhập vào:" )
    trip_graph.update_state(thread, {"accommodation_query": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())
        if count == 4:
            if 'accommodation_response' in current_state:
                print('Chainlit\n')
                print(current_state['accommodation_response'])

    human = input("Hãy nhập vào tên địa điểm bạn muốn lưu trú: ")
    trip_graph.update_state(thread, {"user_accommodation_choice": human})
    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count ==6:  # accommodation_agent
            if 'event_response' in current_state:
                print('Chainlit\n')
                print(current_state['event_response'])

    human = input("Hãy nhập vào tên sự kiện bạn muốn tham quan: ")
    human = process_event_choice_chain.invoke({"input": human})
    trip_graph.update_state(thread, {"user_event_choice": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 8:  # event_agent
            if 'places_response' in current_state:
                print('Chainlit\n')
                print(current_state['places_response'])

    human = input("Hãy nhập vào tên địa điểm bạn muốn tham quan: ")
    human = process_places_choice_chain.invoke({"input": human})
    trip_graph.update_state(thread, {"user_places_choice": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 10:  # places_agent
            if 'food_response' in current_state:
                print('Chainlit\n')
                print(current_state['food_response'])
    human = input("Hãy nhập vào tên món ăn bạn muốn ăn: ")
    human = process_food_choice_chain.invoke({"input": human})
    trip_graph.update_state(thread, {"user_food_choice": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 12:  # food_agent
            if 'transport_response' in current_state:
                print('Chainlit\n')
                print(current_state['transport_response'])
    human = input("Hãy nhập vào phương tiện di chuyển bạn muốn đi: ")
    trip_graph.update_state(thread, {"user_transport_choice": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 14:  # transport_agent
            if 'generate_tour_response' in current_state:
                print('Chainlit\n')
                print(current_state['generate_tour_response'])

        if count == 15:  # price_agent
            if 'price_response' in current_state:
                print('Chainlit\n')
                print(current_state['price_response'])

elif count == 3:
    print(f"\n Trên đây là các tour phù hợp nhất cho kế hoạch du lịch của bạn. Bạn có cảm thấy hài lòng với những tour đã gợi ý hay không?")
    print("\t - Nếu có, hãy chọn tour phù hợp với bạn (VD: Tour 1/2).")
    print("\t - Nếu không, tôi sẽ hỗ trợ bạn xây dựng một tour với những địa điểm tham quan và món ăn nổi bật mà bạn muốn.")
    print("\t - Nếu bạn muốn chỉnh sửa đôi chút, hãy mô tả chi tiết (địa điểm, thời gian, phương tiện,... cần thay đổi)")
    human = input("\n Nhập vào sự lựa chọn của bạn: ")
    trip_graph.update_state(thread, {"recommend_chat": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 5:  # check_adjust node
          if 'completion_tour_response' in current_state:
              print('Chainlit\n')
              print(current_state['completion_tour_response'])
          elif 'adjust_tour_response' in current_state:
              print('Chainlit\n')
              print(current_state['adjust_tour_response'])
        
        if count == 6:  # completion_tour_agent
          if 'completion_tour_response' in current_state:
              print('Chainlit\n')
              print(current_state['completion_tour_response'])
    print(count)     
if count == 5:    
    print("\n Bây giờ chúng tôi sẽ hỗ trợ bạn tạo một tour theo với các hoạt động trải nghiệm ý muốn của bạn nhé! \n")
    print("Chúng tôi sẽ đề xuất lần lượt cho bạn các thông tin về thời tiết, sự kiện, nơi lưu trú, các địa điểm tham quan, các món ăn/ đồ uống ngon và các hình thức di chuyển.\n")
    print("Tiếp theo, bạn hãy trả lời cho tôi biết những danh sách địa điểm, sự kiện, món ăn, nơi lưu trú, phương tiện di chuyển, ... để chúng tôi hỗ trợ bạn sắp xếp 1 tour hoàn chỉnh nhất.")
    print("Lưu ý với mỗi danh sách các sự lọn chọn của bạn hãy cách nhau bằng dấu ',' ")
    print("Đầu tiên hãy cho chúng tôi biết cụ thể hơn về loại hình bạn muốn lưu trú (hotel/ homestay/ resort/ ... ), chất lượng số sao mong muốn và giá phòng/ đêm phù hợp với ngân sách của bạn:")
    human = input("Nhập vào:" )
    trip_graph.update_state(thread, {"accommodation_query": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 7:  # accommodation_agent
            if 'accommodation_response' in current_state:
                print('Chainlit\n')
                print(current_state['accommodation_response'])
                
    human = input("Hãy nhập vào tên địa điểm bạn muốn lưu trú: ")
    trip_graph.update_state(thread, {"user_accommodation_choice": human})
    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 9:  # event_agent
            if 'event_response' in current_state:
                print('Chainlit\n')
                print(current_state['event_response'])

    human = input("Hãy nhập vào tên sự kiện bạn muốn tham quan: ")
    human = process_event_choice_chain.invoke({"input": human})
    trip_graph.update_state(thread, {"user_event_choice": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 11:  # places_agent
            if 'places_response' in current_state:
                print('Chainlit\n')
                print(current_state['places_response'])

    human = input("Hãy nhập vào tên địa điểm bạn muốn tham quan: ")
    human = process_places_choice_chain.invoke({"input": human})
    trip_graph.update_state(thread, {"user_places_choice": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 13:  # food_agent
            if 'food_response' in current_state:
                print('Chainlit\n')
                print(current_state['food_response'])
    human = input("Hãy nhập vào tên món ăn bạn muốn ăn: ")
    human = process_food_choice_chain.invoke({"input": human})
    trip_graph.update_state(thread, {"user_food_choice": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 15:  # transport_agent
            if 'transport_response' in current_state:
                print('Chainlit\n')
                print(current_state['transport_response'])
    human = input("Hãy nhập vào phương tiện di chuyển bạn muốn đi: ")
    trip_graph.update_state(thread, {"user_transport_choice": human})

    for event in trip_graph.stream(None, thread, stream_mode="values"):
        current_state = event
        count += 1
        print('State', count)
        print(current_state)
        print(current_state.keys())

        if count == 17:  # generate_tour_agent
            if 'generate_tour_response' in current_state:
                print('Chainlit\n')
                print(current_state['generate_tour_response'])

        if count == 18:  # price_response
            if 'price_response' in current_state:
                print('Chainlit\n')
                print(current_state['price_response'])

