# Bộ điều khiển thí nghiệm Lab-First

[English](../../en/architecture/controller.md) · [Tài liệu](../index.md)

Mẫu thử EP4CE6E22C8N không có SDRAM ngoài. EP4CE10E22C8N là mục tiêu thiết bị đo trong tương lai. Xem [kiến trúc Lab-First](https://github.com/cirnetlab/cirnet-remote/blob/13a35145b6d15644c7be10d95a5410bf69e11867/docs/ARCHITECTURE.md).

[Mô-đun điều khiển](../../../rtl/experiment-controller/top.v) là khung có thể biên dịch. Hardware Service phụ trách FpgaTransport trên Mini PC. Bộ điều hợp Serial và USB-SPI, giải mã truyền tải vật lý, phép đo tô pô, ma trận chuyển mạch và mạch bảo vệ chưa có trong phạm vi triển khai.

Bộ điều khiển trừu tượng đi qua SAFE → SCANNING → SCANNED → PREPARED → ROUTED → POWERED → ARMED → RUNNING. Quét thành công chỉ xác nhận sẵn sàng quan sát. Điều kiện cho phép cấp nguồn phụ thuộc vào tích hợp an toàn đã được xác minh. Một cờ Boolean riêng lẻ không xác lập an toàn điện.

Reset đưa bộ điều khiển về SAFE và tắt đầu ra, định tuyến cùng xung nhịp. Định tuyến chỉ là hạ tầng và mạch mặc định hở. Đầu ra yêu cầu kế hoạch an toàn, định tuyến sẵn sàng, bảo vệ độc lập và watchdog hoạt động. Mất điều kiện cho phép, xung lỗi hoặc watchdog chặn đầu ra ngay và giữ FAULT. Reset sau khi lỗi đã hết vô hiệu hóa kết quả quét và kế hoạch trước. Chuỗi hoặc lệnh sai làm đầu ra tắt. Chu kỳ dùng nhịp điều khiển trừu tượng.

Tích hợp vật lý cần sơ đồ và chân chính xác, ma trận chuyển mạch và bảo vệ đầu ra, khóa liên động, reset, watchdog, đồng bộ, giới hạn xung, xung nhịp và các giới hạn đã đo. Tổng hợp và định thời trên FPGA đích còn chờ bằng chứng. Xem [kiểm chứng](../verification.md) cho các bài mô phỏng reset, chuỗi sai, lỗi, mọi điều kiện cho phép, STOP, SAFE_STATE và thiết bị đo chưa khả dụng.
