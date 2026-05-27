 const API = "http://127.0.0.1:5000"

// ---------------- REGISTER ----------------

async function register(){

    let username = document.getElementById('username').value
    let email = document.getElementById('email').value
    let password = document.getElementById('password').value
    let confirm = document.getElementById('confirm').value

    if(password !== confirm){
        alert("Passwords not match")
        return
    }

    let res = await fetch(`${API}/register`,{
        method:'POST',
        headers:{
            'Content-Type':'application/json'
        },
        credentials:'include',
        body:JSON.stringify({
            username,
            email,
            password
        })
    })

    let data = await res.json()

    alert(data.message)

    if(res.status === 201){
        window.location='login.html'
    }
}

// ---------------- LOGIN ----------------

async function login(){

    let email = document.getElementById('email').value
    let password = document.getElementById('password').value

    let res = await fetch(`${API}/login`,{
        method:'POST',
        headers:{
            'Content-Type':'application/json'
        },
        credentials:'include',
        body:JSON.stringify({
            email,
            password
        })
    })

    let data = await res.json()

    if(res.status === 200){
        window.location='dashboard.html'
    }else{
        alert(data.message)
    }
}

// ---------------- LOGOUT ----------------

async function logout(){

    try{

        let response = await fetch(
            "http://127.0.0.1:5000/logout",
            {
                method:'GET',
                credentials:'include'
            }
        )

        let data = await response.json()

        alert(data.message)

        window.location = "/"

    }

    catch(error){

        console.log(error)

        alert("Logout failed")
    }
}

// ---------------- DASHBOARD ----------------

async function loadDashboard(){

    let res = await fetch(`${API}/expenses/summary`,{
        credentials:'include'
    })

    if(res.status === 401){
        window.location='login.html'
        return
    }

    let data = await res.json()

    document.getElementById('welcome').innerHTML =
        `Welcome ${data.username}`

    document.getElementById('total').innerHTML =
        data.total

    document.getElementById('highest').innerHTML =
        data.highest

    document.getElementById('count').innerHTML =
        data.count

    let categoryDiv = document.getElementById('categories')

    categoryDiv.innerHTML = ""

    data.categories.forEach(cat=>{

        categoryDiv.innerHTML += `
            <p>${cat.category} - ₹${cat.total}</p>

            <div class="bar">
                <div class="fill"
                style="width:${cat.total}%">
                    ${cat.total}
                </div>
            </div>
        `
    })
}

// ---------------- LOAD EXPENSES ----------------

async function loadExpenses(){

    let response = await fetch(
        "http://127.0.0.1:5000/expenses",
        {
            credentials:'include'
        }
    )

    let expenses = await response.json()

    showExpenses(expenses)
}
// ---------------- SHOW EXPENSES ----------------

function showExpenses(expenses){

    let container =
        document.getElementById('expenseTree')

    container.innerHTML = ""

    // IF NO DATA

    if(expenses.length === 0){

        container.innerHTML = `

            <p style="
                margin-top:20px;
                color:#94a3b8;
                font-size:18px;
            ">
                No expenses added yet
            </p>
        `

        return
    }

    // GROUP BY TITLE

    let grouped = {}

    expenses.forEach(expense=>{

        if(!grouped[expense.title]){

            grouped[expense.title] = []
        }

        grouped[expense.title].push(expense)
    })

    // DISPLAY

    for(let title in grouped){

        container.innerHTML += `

        <div class="tree-box">

            <div class="main-title">

                ${title}

            </div>

            ${grouped[title].map(expense => `

                <div class="branch">

                    <div class="expense-card">

                        <div class="expense-info">

                            <div class="expense-category">

                                ${expense.category}

                            </div>

                            <div class="expense-amount">

                                ₹${expense.amount}

                            </div>

                            <div class="expense-date">

                                ${new Date(expense.date).toLocaleDateString("en-GB", {
                                day: "2-digit",
                                month: "short",
                                year: "numeric"
                                })}

                            </div>

                            <div class="expense-note">

                                ${expense.note || ""}

                            </div>

                        </div>

                        <div class="action-group">

                            <button class="action-btn edit-btn"
                            onclick='editExpense(${JSON.stringify(expense)})'>

                                Edit

                            </button>

                            <button class="action-btn delete-btn"
                            onclick='deleteExpense(${expense.id})'>

                                Delete

                            </button>

                        </div>

                    </div>

                </div>

            `).join('')}

        </div>
        `
    
    }
}
// ---------------- SAVE EXPENSE ----------------

async function saveExpense(){

    let id = document.getElementById('expenseId').value

    let expense = {
        title:document.getElementById('title').value,
        amount:document.getElementById('amount').value,
        category:document.getElementById('category').value,
        date:document.getElementById('date').value,
        note:document.getElementById('note').value
    }

    let url = `${API}/expenses`
    let method = "POST"

    if(id){
        url = `${API}/expenses/${id}`
        method = "PUT"
    }

    let res = await fetch(url,{
        method,
        headers:{
            'Content-Type':'application/json'
        },
        credentials:'include',
        body:JSON.stringify(expense)
    })

    let data = await res.json()

    alert(data.message)

    loadExpenses()

    document.getElementById('expenseId').value = ""
}

// ---------------- EDIT ----------------

function editExpense(expense){

    document.getElementById('expenseId').value =
        expense.id

    document.getElementById('title').value =
        expense.title

    document.getElementById('amount').value =
        expense.amount

    document.getElementById('category').value =
        expense.category

    document.getElementById('date').value =
        expense.date

    document.getElementById('note').value =
        expense.note
}

// ---------------- DELETE ----------------

async function deleteExpense(id){

    let confirmDelete = confirm("Delete Expense?")

    if(!confirmDelete) return

    await fetch(`${API}/expenses/${id}`,{
        method:'DELETE',
        credentials:'include'
    })

    loadExpenses()
}

// ---------------- FILTER ----------------

async function filterExpenses(){

    let category =
        document.getElementById('filterCategory').value

    let from =
        document.getElementById('from').value

    let to =
        document.getElementById('to').value

    let url = `${API}/expenses/filter?`

    if(category){
        url += `category=${category}&`
    }

    if(from && to){
        url += `from=${from}&to=${to}`
    }

    let res = await fetch(url,{
        credentials:'include'
    })

    let expenses = await res.json()

    showExpenses(expenses)
}
function searchExpenses(){

    let input = document
        .getElementById("searchInput")
        .value
        .toLowerCase();

    let cards = document.querySelectorAll(".expense-card");

    cards.forEach(card => {

        let text = card.innerText.toLowerCase();

        if(text.includes(input)){
            card.style.display = "flex";
        }
        else{
            card.style.display = "none";
        }

    });

}