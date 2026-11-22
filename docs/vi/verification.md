# Kiểm chứng và đóng gói RTL

[English](../en/verification.md) · [Tài liệu](index.md)

Dùng Node 26 và Python 3.14. Chọn biên nhận native, crate và mô-đun cấp phát bên ngoài do Contracts tạo. Cung cấp SHA-256 đã rà soát và cấp phát một phiên bên ngoài. Cài phụ thuộc kiểm chứng trong môi trường ảo bên ngoài bằng `python -m pip install --require-hashes -r requirements-verification.lock`.

```powershell
$env:CIRNET_NATIVE_CONTRACTS_RECEIPT = $contractsReceipt
$env:CIRNET_NATIVE_CONTRACTS_SHA256 = $contractsSha256
$env:CIRNET_NATIVE_CONTRACTS_CRATE = $contractsCrate
$env:CIRNET_ARTIFACTS_CLI = $allocator
$env:CIRNET_ARTIFACTS_CLI_SHA256 = $allocatorSha256
$env:CIRNET_ARTIFACTS_CONTEXT = node $allocator --context-info
$env:CIRNET_ARTIFACTS_SESSION = node $allocator
python -B scripts/install_toolchain.py
```

Đặt `CIRNET_FPGA_TOOLCHAIN_ROOT` thành thư mục cài đặt do script in ra hoặc chọn bộ công cụ đã ghim tương ứng. Cổng kiểm chứng xác thực gói và các phụ thuộc thực thi trước khi chạy slang và mô phỏng Icarus.

```powershell
python -B -m pytest --basetemp (Join-Path $env:CIRNET_ARTIFACTS_SESSION 'pytest')
node --test tests/build-source.test.mjs
$filename = "cirnet-embedded-hardware-$(Get-Content VERSION)-native-source.tar.gz"
node scripts/build-source.mjs --output (Join-Path $env:CIRNET_ARTIFACTS_SESSION $filename) --contracts-receipt $contractsReceipt --contracts-sha256 $contractsSha256
```

Cả `LAB_FIRST_RTL_PASS` và `PERMIT_MATRIX_RTL_PASS` phải đến từ mô phỏng thật. Gói chứa RTL, testbench và danh mục tệp trong `fpga-artifact.json`; bước đóng gói ghi mã băm của biên nhận Contracts và schema logic đã chọn. Bitstream, thời gian, bảo vệ điện và kiểm chứng trên phần cứng cần bằng chứng cho bo mạch cụ thể.
