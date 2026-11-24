# CIRNET Embedded Hardware v0

## 0.3.0-dev.1 (development)

- Give the installer and RTL verification commands a common module for pinned toolchain checks. Document the RTL, testbench and tool responsibilities.
- Dùng chung mô-đun kiểm tra bộ công cụ đã ghim cho lệnh cài đặt và kiểm chứng RTL. Ghi rõ trách nhiệm của RTL, testbench và các công cụ.
- Migrate the controller and instrument RTL and both behavioral testbenches. Bind source candidates to the native Contracts receipt.
- Chuyển RTL bộ điều khiển, thiết bị đo và cả hai testbench hành vi. Gắn ứng viên mã nguồn với biên nhận Contracts native.
- Link the verified RTL scaffold to the FPGA and CIRNET Lab-First targets.
- Liên kết RTL scaffold đã kiểm chứng với kiến trúc đích FPGA và CIRNET Lab-First.
- Verify allocator session reuse and digest rejection, late scanner replies, and reset with an active interlock fault.
- Kiểm chứng việc dùng lại phiên cấp phát và từ chối mã băm sai, phản hồi quét đến muộn và reset khi lỗi liên động còn tồn tại.
- Document offline RTL verification with the selected native Contracts receipt, hash-pinned wheels and OSS CAD Suite archive.
- Ghi lại quy trình kiểm chứng RTL ngoại tuyến với biên nhận Contracts native, các wheel và gói OSS CAD Suite đã ghim mã băm.
