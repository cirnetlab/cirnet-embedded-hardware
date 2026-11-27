# Duy trì tài liệu CIRNET FPGA

[English](../../en/contributing/writing-documentation.md) · [Tài liệu](../index.md) · [Quy định của kho](../../../AGENTS.md)

Giữ README gốc bằng tiếng Anh và dẫn đến hai mục lục. Giữ các trang hiện hành ở đường dẫn tương ứng trong `docs/en/` và `docs/vi/`. Cập nhật từng cặp cùng lúc và giữ nguyên định danh, lệnh, giới hạn và trạng thái khả năng giữa hai ngôn ngữ. FPGA sở hữu RTL, mô phỏng và đóng gói mã nguồn. Contracts sở hữu schema logic, Hardware Service phụ trách lớp truyền tải riêng, còn Remote phụ trách tích hợp hệ thống và lựa chọn phát hành. [Hướng dẫn khung RTL](../scaffold.md)

Dùng một tệp `CHANGELOG_V<major>.md` cho mỗi phiên bản chính đã phát hành. Đặt Unreleased trước các bản phát hành, rồi liệt kê chúng theo thứ tự giảm dần. Mỗi bản có tiêu đề SemVer, liên kết từ mục lục, ngày có bằng chứng và commit đích của tag. Phân biệt gói đã phát hành, bản dựng ứng viên và checkout hiện tại. [Nhật ký phát hành](../../changelogs/README.md)


Giữ hồ sơ kiểm chứng và di chuyển theo ngày ở đường dẫn đã ghi và bằng ngôn ngữ gốc. Bảo toàn neo README, định danh công cụ và artifact đã duyệt, cùng tham chiếu tương thích. Trước khi di chuyển tài liệu, truy vết tham chiếu trong Markdown, mã nguồn, kiểm thử, CI và quy trình đóng gói. Dẫn hồ sơ đã được thay thế bằng revision Git cố định.

Đối chiếu các cặp ngôn ngữ bị ảnh hưởng, đường dẫn liên kết, chữ hoa thường, neo tiêu đề và tham chiếu liên kho. Ghi revision, đầu vào và phạm vi của kết quả kiểm chứng. Giữ bằng chứng thô trong phiên do bộ cấp phát quản lý, nằm ngoài checkout, worktree và thư mục Git. Sau kiểm chứng, cập nhật các trang kỹ thuật và nhật ký liên quan rồi rà soát Git diff, trạng thái và đầu ra bị bỏ qua. [Hướng dẫn kiểm chứng](../verification.md)
