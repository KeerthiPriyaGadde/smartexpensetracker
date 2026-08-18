
// Load transactions when dashboard opens
document.addEventListener("DOMContentLoaded", loadTransactions);


// Add Transaction
async function addTransaction() {

    const type = document.getElementById("type").value;
    const category = document.getElementById("category").value;
    const amount = document.getElementById("amount").value;
    const description = document.getElementById("description").value;

    if (!amount || amount <= 0) {
        alert("Please enter a valid amount");
        return;
    }

    const response = await fetch("/add_transaction", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            type: type,
            category: category,
            amount: amount,
            description: description
        })
    });

    const result = await response.json();

    if (response.ok) {

        alert("Transaction added successfully!");

        document.getElementById("amount").value = "";
        document.getElementById("description").value = "";

        loadTransactions();

    } else {

        alert(result.error || "Something went wrong");

    }
}


// Load Transactions
async function loadTransactions() {

    const response = await fetch("/transactions");

    if (!response.ok) {
        return;
    }

    const transactions = await response.json();

    const table = document.getElementById("transactionTable");

    table.innerHTML = "";

    let totalIncome = 0;
    let totalExpense = 0;

    transactions.forEach(transaction => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${transaction.type}</td>
            <td>${transaction.category}</td>
            <td>₹${transaction.amount}</td>
            <td>${transaction.description || ""}</td>
            <td>${transaction.transaction_date}</td>
            <td>
                <button onclick="deleteTransaction(${transaction.id})">
                    Delete
                </button>
            </td>
        `;

        table.appendChild(row);

        if (transaction.type === "income") {
            totalIncome += Number(transaction.amount);
        }

        if (transaction.type === "expense") {
            totalExpense += Number(transaction.amount);
        }

    });

    document.getElementById("income").innerText =
        "₹" + totalIncome;

    document.getElementById("expense").innerText =
        "₹" + totalExpense;

    document.getElementById("balance").innerText =
        "₹" + (totalIncome - totalExpense);
}


// Delete Transaction
async function deleteTransaction(id) {

    const confirmDelete = confirm(
        "Are you sure you want to delete this transaction?"
    );

    if (!confirmDelete) {
        return;
    }

    const response = await fetch(
        "/delete_transaction/" + id,
        {
            method: "DELETE"
        }
    );

    if (response.ok) {

        alert("Transaction deleted successfully!");

        loadTransactions();

    } else {

        alert("Failed to delete transaction");

    }
}