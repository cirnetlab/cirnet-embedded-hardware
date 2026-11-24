# Kiểm chứng các testbench RTL

[English](../../en/guides/testbenches.md) · [Tài liệu](../index.md)

Các testbench kiểm tra RTL độc lập với VirtualHardwareStation. [Hướng dẫn kiểm chứng](../verification.md) định danh bộ công cụ đã ghim. Pytest gọi trình kiểm tra RTL. Thiếu hoặc sai slang, trình biên dịch hay trình chạy là lỗi.

`tb_lab_first_control.v` giữ reset qua một cạnh xung trước khi nhả. `tb_permit_matrix.v` kiểm tra mọi điều kiện cho phép bị mất, SAFE_STATE, STOP, quét thất bại, chu kỳ bằng không, ranh giới xung và các yêu cầu thiết bị chưa hỗ trợ. Hai dấu hiệu bắt buộc từ mô phỏng là `LAB_FIRST_RTL_PASS` và `PERMIT_MATRIX_RTL_PASS`.

Mỗi lần chạy giữ một thư mục riêng gồm mã băm nguồn, danh tính bộ công cụ và nhật ký. Cấu hình, thư viện và mã thực thi được đối chiếu với gói đã xác thực. Bài kiểm tra phân biệt chặn đầu ra tức thời với dọn trạng thái FAULT và định tuyến theo xung.

Phạm vi là điều khiển trừu tượng. Bảo vệ điện, chân, máy quét, định thời ADC/DAC/SDRAM, tổng hợp trên đích, CDC, thu nhận thật và việc chạy trên Linux cần bằng chứng riêng.
