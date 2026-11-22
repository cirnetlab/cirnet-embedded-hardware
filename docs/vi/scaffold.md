# Khung bộ điều khiển và thiết bị đo

[English](../en/scaffold.md) · Tiếng Việt

[Mục lục tài liệu](index.md)

[Kiến trúc FPGA](https://github.com/cirnetlab/cirnet-remote-next/blob/master/docs/cirnetlab-FPGA-architecture-vi.md) định nghĩa đích thiết kế bo trong phạm vi [quy tắc an toàn Lab-First](https://github.com/cirnetlab/cirnet-remote-next/blob/master/docs/cirnet-architecture-lab-first-vi.md).

| Bên sở hữu | Ranh giới |
| --- | --- |
| FPGA | RTL Verilog/SystemVerilog của bộ điều khiển và thiết bị đo, thiết kế định thời, kích hoạt và thu tín hiệu, giao diện SDRAM/CDC và bằng chứng theo từng bo. Mã nguồn này cung cấp khung bộ điều khiển và các testbench RTL. |
| Hardware | Trình điều khiển trạm cục bộ, lớp truyền tải FPGA nội bộ và bảo vệ tại trạm. |
| Contracts và Remote | Contracts sở hữu schema logic `1.0-scaffold` và phiên bản bản đồ thanh ghi dành sẵn. Remote sở hữu API Web, bộ lập lịch, phân quyền và lựa chọn bản phát hành Lab. |

Mẫu thử hướng tới EP4CE6E22C8N không có SDRAM ngoài. Trong mô phỏng, bộ điều khiển đi qua SAFE → SCANNING → SCANNED → PREPARED → ROUTED → POWERED → ARMED → RUNNING. Quét thành công cho biết bước quan sát đã sẵn sàng. An toàn điện và tính đúng của tô pô vẫn được kiểm tra riêng.

Reset đưa bộ điều khiển về SAFE và tắt điều khiển đầu ra, định tuyến, xung nhịp thí nghiệm. Trước khi cho phép điều khiển đầu ra, bộ điều khiển mô phỏng yêu cầu kế hoạch an toàn, định tuyến sẵn sàng, bảo vệ độc lập và watchdog đã kích hoạt. Các điều kiện này tiếp tục được kiểm tra trong khi chạy. Tín hiệu lỗi hoặc watchdog chặn đầu ra ngay và giữ trạng thái FAULT. Reset sau khi hết lỗi vô hiệu hóa kết quả quét và kế hoạch cũ. Xung nhịp thí nghiệm tính theo nhịp điều khiển trừu tượng. Xem [đặc tả bộ điều khiển](architecture/controller.md).

Mục tiêu EP4CE10E22C8N với SDRAM ngoài dành sẵn giao diện cho Logic Analyzer, Scope 2CH, Generator 2CH, SDRAM Arbiter, Trigger, Timestamp và CDC. Cờ khả dụng, cờ dữ liệu thu hợp lệ, cho phép phát tín hiệu và yêu cầu SDRAM đều ở mức false. Các cổng xung nhịp của từng miền chưa xác định tần số bo mạch. Xem [giao diện thiết bị đo](architecture/instrument.md).

Firmware và truyền tải vật lý vẫn là `UNAVAILABLE`. Đóng gói mã nguồn và mô phỏng RTL bao phủ phần khung. Bitstream, định thời, bảo vệ và HIL cần bằng chứng của từng bo. Trước khi kích hoạt phần cứng, cần có sơ đồ bo mạch, phân chân, giới hạn điện, ADC/DAC và SDRAM đã chọn, ràng buộc thời gian, phương án xung nhịp và reset, cùng kết quả đo bảo vệ và thu nhận. Các đầu vào này vẫn là `TBD_BY_HARDWARE_DESIGN`. Hardware Service phụ trách giao tiếp nội bộ. Bộ điều hợp Serial và USB-SPI phụ thuộc vào việc chọn phần cứng thật.
