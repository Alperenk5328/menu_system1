document.addEventListener("DOMContentLoaded", function () {
    let cart = {};

    // Artı ve Eksi Butonları
    document.querySelectorAll(".increase").forEach(button => {
        button.addEventListener("click", function () {
            let quantityInput = this.previousElementSibling;
            quantityInput.value = parseInt(quantityInput.value) + 1;
        });
    });

    document.querySelectorAll(".decrease").forEach(button => {
        button.addEventListener("click", function () {
            let quantityInput = this.nextElementSibling;
            if (parseInt(quantityInput.value) > 1) {
                quantityInput.value = parseInt(quantityInput.value) - 1;
            }
        });
    });

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

