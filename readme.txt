Mô tả hệ thống:
Hệ thống đa tác nhân (Multi-agent LLM) để tối ưu hóa lịch trình du lịch. Hệ thống được xây dựng với các thành phần bao gồm các tác nhân độc lập, công cụ hỗ trợ và các phần mở rộng cho nhiều tính năng. Dưới đây là mô tả chi tiết về các thành phần của hệ thống.

Cấu trúc Thư mục:
- state.py: Định nghĩa trạng thái hệ thống bằng TypeDict, lưu trữ và quản lý các thông tin trạng thái của hệ thống.
- workflow.py: Định nghĩa đồ thị kiến trúc hệ thống (StateGraph) để điều phối các tác nhân và các bước xử lý.
- tools.py: Các công cụ mà các tác nhân trong hệ thống sử dụng để thực hiện các nhiệm vụ, tính toán, và hỗ trợ quá trình xử lý.
- tsp_algorithm.py: Triển khai thuật toán giải quyết bài toán TSP, tối ưu hóa lịch trình du lịch với các giới hạn về khoảng cách và số lượng điểm đến mỗi ngày.
- trip_info_team/: Thư mục chứa các tác nhân phụ thuộc vào thông tin chuyến đi.
- recommend_tour_team/: Thư mục chứa các tác nhân phụ trách đề xuất tour du lịch.
- create_tour_team/: Thư mục chứa các tác nhân tạo tour du lịch.
- main.py: Mã thực thi chương trình chính, nơi nhập thông tin vào các input đã được định nghĩa sẵn và thực hiện quá trình tối ưu hóa.
- app_workflow.py: Mã quản lý đồ thị kiến trúc hệ thống tùy chỉnh, dùng để triển khai giao diện người dùng.
- app.py: Mã triển khai giao diện người dùng chatbot với Chainlit, cho phép tương tác với hệ thống thông qua UI dễ sử dụng.

Các bước cài đặt và chạy hệ thống:
1. Khởi tạo môi trường ảo:
Trước tiên, bạn cần khởi tạo môi trường ảo để cài đặt các thư viện và phụ thuộc cần thiết cho hệ thống:
python -m venv .venv
2. Cài đặt các thư viện phụ thuộc:
Cài đặt các thư viện cần thiết bằng cách chạy lệnh sau:

Dưới đây là phiên bản viết liền mạch và liên tục cho file README.txt:

less
Copy code
Hệ thống tối ưu hóa lịch trình du lịch - README

Mô tả hệ thống:
Hệ thống này sử dụng thuật toán tối ưu hóa cho bài toán TSP (Traveling Salesman Problem) và các tác nhân đa nhiệm (Multi-agent) để tối ưu hóa lịch trình du lịch. Hệ thống được xây dựng với các thành phần bao gồm các tác nhân độc lập, công cụ hỗ trợ và các phần mở rộng cho nhiều tính năng. Dưới đây là mô tả chi tiết về các thành phần của hệ thống.

Cấu trúc Thư mục:
- state.py: Định nghĩa trạng thái hệ thống bằng TypeDict, lưu trữ và quản lý các thông tin trạng thái của hệ thống.
- workflow.py: Định nghĩa đồ thị kiến trúc hệ thống (StateGraph) để điều phối các tác nhân và các bước xử lý.
- tools.py: Các công cụ mà các tác nhân trong hệ thống sử dụng để thực hiện các nhiệm vụ, tính toán, và hỗ trợ quá trình xử lý.
- tsp_algorithm.py: Triển khai thuật toán giải quyết bài toán TSP, tối ưu hóa lịch trình du lịch với các giới hạn về khoảng cách và số lượng điểm đến mỗi ngày.
- trip_info_team/: Thư mục chứa các file khai báo các tác nhân và prompt tương ứng với nhiệm vụ phản hồi thông tin chuyến đi.
- recommend_tour_team/: Thư mục chứa các file khai báo các tác nhân và prompt phụ trách đề xuất tour du lịch.
- create_tour_team/: Thư mục chứa các file khai báo các tác nhân và prompt tương ứng với chức năngnăng tạo tour du lịch.
- main.py: Mã thực thi chương trình chính, nơi nhập thông tin vào các input đã được định nghĩa sẵn và thực hiện quá trình tối ưu hóa.
- app_workflow.py: Mã quản lý đồ thị kiến trúc hệ thống tùy chỉnh, dùng để triển khai giao diện người dùng.
- app.py: Mã triển khai giao diện người dùng chatbot với Chainlit, cho phép tương tác với hệ thống thông qua UI dễ sử dụng.

Các bước cài đặt và chạy hệ thống:
1. Khởi tạo môi trường ảo:
Trước tiên, bạn cần khởi tạo môi trường ảo để cài đặt các thư viện và phụ thuộc cần thiết cho hệ thống: python -m venv .venv

Thực hiện khởi tạo .venv: 
- Đối với Window: .\.venv\Scripts\activate
- Đối với macOS/Linux: source .venv/bin/activate

2. Cài đặt các thư viện phụ thuộc:
Cài đặt các thư viện cần thiết bằng cách chạy lệnh sau: pip install -r requirements.txt

3. Chạy hệ thống qua terminal:
Sau khi cài đặt xong, bạn có thể chạy hệ thống thông qua terminal với lệnh: python main.py

4. Chạy hệ thống với giao diện chatbot:
Nếu bạn muốn sử dụng giao diện người dùng chatbot, có thể chạy hệ thống với lệnh sau: chainlit run app.py

Lưu ý rằng giao diện chatbot có thể mất nhiều thời gian hơn do quá trình xử lý các tác nhân không đồng bộ.

