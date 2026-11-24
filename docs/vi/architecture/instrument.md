# Miền thiết bị đo EP4CE10

[English](../../en/architecture/instrument.md) · [Tài liệu](../index.md)

Mục tiêu là EP4CE10E22C8N với SDRAM ngoài. [Giao diện RTL](../../../rtl/instrument/top.v) giữ cờ khả dụng, dữ liệu thu hợp lệ, cho phép phát và yêu cầu SDRAM ở mức thấp.

| Ranh giới | Triển khai và bằng chứng cần có |
| --- | --- |
| Bộ phân tích logic | Điều hòa đầu vào số, đóng gói mẫu, bộ đệm giới hạn và tốc độ đo được |
| Máy hiện sóng hai kênh | ADC, độ phân giải, giao diện, AFE, dải đo, ghép nối, bảo vệ và hiệu chuẩn |
| Bộ phát hai kênh | DAC, giao diện, tầng đầu ra, bộ nhớ dạng sóng, bảo vệ và hiệu chuẩn |
| Phân xử SDRAM | Linh kiện, tổ chức bộ nhớ, định thời theo datasheet, làm tươi, phân xử và chống tràn |
| Trigger | Kênh, sườn, mức, trạng thái sẵn sàng và vùng đệm trước/sau trigger |
| Timestamp | Nguồn xung, độ rộng bộ đếm, hành vi tràn và độ phân giải đo được |
| CDC | Miền điều khiển, thu, phát và SDRAM, nhả reset, handshake/FIFO và ràng buộc |

Các cổng `control_clk`, `acquisition_clk`, `generator_clk` và `sdram_clk` chỉ đặt tên miền xung. Thiết kế chưa xác lập tần số hay trả về mẫu và xác nhận giả. Các thông số điện, chân và định thời vẫn là `TBD_BY_HARDWARE_DESIGN`. Cần công bố sơ đồ, datasheet, kế hoạch PLL/xung/reset, giới hạn thu/phát, kiểm tra SDRAM, bảo vệ, khóa liên động và kết quả định thời Quartus trước khi bật từng năng lực.
