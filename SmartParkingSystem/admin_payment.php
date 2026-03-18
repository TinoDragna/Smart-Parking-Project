<?php

$db = new mysqli("localhost","smartparking","cyber@2025","smart_parking");

if(isset($_POST['confirm'])){

    $id = intval($_POST['id']);

    $db->query("UPDATE payments SET Status='paid' WHERE PaymentID=$id");

}

$res = $db->query("SELECT * FROM payments ORDER BY PaymentID DESC");

?>

<h2>Admin Payment</h2>

<table border=1>

<tr>
<th>ID</th>
<th>RFID</th>
<th>Amount</th>
<th>Status</th>
<th>Action</th>
</tr>

<?php while($r=$res->fetch_assoc()){ ?>

<tr>

<td><?php echo $r['PaymentID']; ?></td>

<td><?php echo $r['RFID']; ?></td>

<td><?php echo $r['Amount']; ?></td>

<td><?php echo $r['Status']; ?></td>

<td>

<?php if($r['Status']=="pending"){ ?>

<form method="POST">

<input type="hidden" name="id" value="<?php echo $r['PaymentID']; ?>">

<button name="confirm">Confirm Paid</button>

</form>

<?php } ?>

</td>

</tr>

<?php } ?>

</table>