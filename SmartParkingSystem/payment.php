<?php

$db = new mysqli("localhost","smartparking","cyber@2025","smart_parking");

$id = intval($_GET['id']);

$res = $db->query("SELECT * FROM payments WHERE PaymentID=$id");

$p = $res->fetch_assoc();

$bank = "vcb";
$account = "123456789";
$name = "SMART PARKING";

$qr = "https://img.vietqr.io/image/$bank-$account-compact.png?amount={$p['Amount']}&addInfo=PAY{$p['PaymentID']}&accountName=$name";

?>

<h2>Thanh toán giữ xe</h2>

<p>RFID: <?php echo $p['RFID']; ?></p>

<p>Số tiền: <?php echo $p['Amount']; ?> VNĐ</p>

<img src="<?php echo $qr ?>" width="300">

<p>Đang chờ thanh toán...</p>

<script>
setTimeout(()=>location.reload(),5000);
</script>