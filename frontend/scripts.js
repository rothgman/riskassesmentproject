// 🔹 1. API base URL
const API_BASE = "http://127.0.0.1:8000/api/borrowers/";

// 🔹 2. Load all borrowers into the table
function loadBorrowers() {
  fetch(API_BASE)
    .then(res => res.json())
    .then(data => {
      const tbody = document.querySelector("#borrowers-table tbody");
      tbody.innerHTML = "";
      data.forEach(b => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${b.id}</td>
          <td><input value="${b.name}" data-id="${b.id}" data-field="name"></td>
          <td><input value="${b.region}" data-id="${b.id}" data-field="region"></td>
          <td><input type="number" value="${b.loan_amount}" data-id="${b.id}" data-field="loan_amount"></td>
          <td>${b.adjusted_score ?? "N/A"}</td>
          <td>${b.risk ?? "N/A"}</td>
          <td>${b.decision ?? "N/A"}</td>
          <td>
  <button onclick="updateBorrower('${b.id}')">💾 Save</button>
  <button onclick="deleteBorrower('${b.id}')">🗑️ Delete</button>
  <button onclick="explainBorrower('${b.id}')">💡 Explain</button>
</td>

        `;
        tbody.appendChild(row);
      });
    });
}

// 🔹 3. Submit new borrower from form
document.querySelector("#borrowerForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const borrower = {
    id: document.querySelector("#id").value,
    name: document.querySelector("#name").value,
    region: document.querySelector("#region").value,
    loan_amount: parseFloat(document.querySelector("#loan_amount").value),
    repayment_rate: parseFloat(document.querySelector("#repayment_rate").value)
  };

  fetch(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(borrower)
  })
    .then(res => res.json())
    .then(data => {
      alert(`✅ Borrower added! Risk: ${data.risk}, Decision: ${data.decision}`);
      loadBorrowers();
    })
    .catch(err => {
      console.error("Error submitting borrower:", err);
      alert("❌ Error adding borrower");
    });
});


// 🔹 ✅ 4. INSERT THESE FUNCTIONS HERE:

function updateBorrower(id) {
  const inputs = document.querySelectorAll(`input[data-id='${id}']`);
  const borrower = { id };
  inputs.forEach(input => {
    const field = input.dataset.field;
    borrower[field] = field === "loan_amount" ? parseFloat(input.value) : input.value;
  });
  borrower.repayment_rate = 0.9; // Dummy or fetch actual

  fetch(API_BASE + id, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(borrower)
  })
    .then(res => res.json())
    .then(() => {
      alert("✅ Borrower updated!");
      loadBorrowers();
    });
}

function explainBorrower(id) {
  const inputs = document.querySelectorAll(`input[data-id='${id}']`);
  const borrower = { id };
  inputs.forEach(input => {
    const field = input.dataset.field;
    borrower[field] = field === "loan_amount" ? parseFloat(input.value) : input.value;
  });
  borrower.repayment_rate = 0.9;

  fetch(API_BASE + "explain/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(borrower)
  })
    .then(res => res.json())
    .then(data => {
      const msg = data.choices?.[0]?.message?.content || "No explanation available.";
      alert("💡 Explanation:\n\n" + msg);
    });
}

function deleteBorrower(id) {
  if (confirm(`Are you sure you want to delete borrower ${id}?`)) {
    fetch(API_BASE + id, { method: "DELETE" })
      .then(res => res.json())
      .then(() => {
        alert("🗑️ Borrower deleted.");
        loadBorrowers();
      });
  }
}


// 🔹 5. Auto-load table on page load
window.onload = loadBorrowers;
