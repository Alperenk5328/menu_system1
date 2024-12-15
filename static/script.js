document.addEventListener("DOMContentLoaded", function () {
    let cart = {};

    // Sipariş ödemesini işaretleme
    function markAsPaid(orderId, productName) {
        fetch('/update_order_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order_id: orderId, product_name: productName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert("Hata: " + data.message);
            }
        })
        .catch(error => console.error("Hata:", error));
    }

    // Masayı silme
    function deleteTable(orderId) {
        if (confirm('Bu masayı silmek istediğinize emin misiniz?')) {
            fetch(`/delete_table/${orderId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Masa başarıyla silindi!");
                    location.reload();
                } else {
                    alert("Hata: " + data.message);
                }
            })
            .catch(error => console.error("Hata:", error));
        }
    }

    // Sipariş miktarını artırma/azaltma
    function updateQuantity(orderId, productName, change) {
        fetch('/update_quantity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order_id: orderId, product_name: productName, change: change })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert("Hata: " + data.message);
            }
        })
        .catch(error => console.error("Hata:", error));
    }

    // Sepete Ekle Butonu
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function () {
            let productName = this.getAttribute("data-name");
            let productPrice = parseFloat(this.getAttribute("data-price"));
            let quantity = parseInt(this.previousElementSibling.querySelector(".quantity").value);

            if (cart[productName]) {
                cart[productName].quantity += quantity;
                cart[productName].totalPrice = cart[productName].quantity * productPrice;
            } else {
                cart[productName] = {
                    quantity: quantity,
                    totalPrice: quantity * productPrice
                };
            }

            updateCart();
        });
    });

    // Sepeti Güncelle
    function updateCart() {
        let cartItemsContainer = document.querySelector(".cart-items");
        cartItemsContainer.innerHTML = "";
        let totalPrice = 0;

        for (let product in cart) {
            let item = cart[product];
            totalPrice += item.totalPrice;

            let itemElement = document.createElement("div");
            itemElement.classList.add("cart-item");
            itemElement.innerHTML = `
                <p data-name="${product}" class="cart-item-text">${product} (x${item.quantity}) - ₺${item.totalPrice.toFixed(2)} 
                    <button class="remove-item">Sil</button>
                </p>
            `;
            cartItemsContainer.appendChild(itemElement);
        }

        document.getElementById("total-price").textContent = `₺${totalPrice.toFixed(2)}`;

        // Sepet görünür hale gelir
        document.querySelector(".cart").style.display = cartItemsContainer.innerHTML ? "block" : "none";

        // Silme Butonlarına Tıklama Olayı
        document.querySelectorAll(".remove-item").forEach(button => {
            button.addEventListener("click", function () {
                let productName = this.closest('p').getAttribute('data-name');
                delete cart[productName];
                updateCart();
            });
        });
    }

    // Siparişi Onayla
    document.getElementById("confirm-order").addEventListener("click", function () {
        const tableNumber = prompt("Masa numarasını giriniz:");
        if (tableNumber) {
            fetch("/add_order", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    table_number: tableNumber,
                    details: JSON.stringify(cart)
                })
            }).then(response => {
                if (response.ok) {
                    alert("Sipariş başarıyla gönderildi!");
                    window.location.reload();
                } else {
                    alert("Bir hata oluştu. Lütfen tekrar deneyiniz.");
                }
            });
        }
    });
});