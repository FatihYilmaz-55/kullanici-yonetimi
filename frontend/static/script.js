const form = document.getElementById('addUserForm');
const userTableBody = document.getElementById('userTableBody');
const formContainer = document.getElementById('kullaniciGiris');
const showFormBtn = document.getElementById('kullaniciGirisiGoster');
const newUserTitle = document.querySelector('.newUser');

let users = [];

function showToast(message, type='error') {
  const toast = document.getElementById('toast');
  if (!toast) {
    console.error('Toast div bulunamadı!');
    return;
  }
  toast.textContent = message;

  toast.classList.remove('success', 'show', 'error');

  toast.classList.add(type)
  toast.classList.add('show');

  if(type === 'success'){
    toast.classList.add('success');
  }else{
    toast.classList.add('error');
  }
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

function showSuccess(message){
    showToast(message, 'success');
}

function showError(message){
    showToast(message, 'error');
}

async function fetchUsers() {
try {
    const response = await fetch("http://localhost:5000/users");
    users = await response.json();

    renderTable();
} catch (error) {
    showError('Kullanıcıları alırken hata oluştu: ' + error.message);
}
}

function renderTable() {
userTableBody.innerHTML = "";

users.forEach(user => {
    const dateObj = new Date(user.created_at);
    const formattedDate = dateObj.toLocaleString('tr-TR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC"
    });
    users.forEach(user => {
    console.log(`ID: ${user.id}, Created At: ${user.created_at}`);  
    });

    const row = document.createElement("tr");
    // Template literal için tırnak işaretlerini düzelttim ve <td> elementlerini string içine aldım
    row.innerHTML = `
    <td>${user.firstName}</td>
    <td>${user.lastName}</td>
    <td>${user.email}</td>
    <td>${formattedDate}</td>
    <td class="action-cell">
        <button class="editBtn" data-id="${user.id}" title="Düzenle">✏️</button>
        <button class="deleteBtn" data-id="${user.id}" title="Sil">🗑️</button>
    </td>
    `;
    userTableBody.appendChild(row);
    users.forEach(user => {
    console.log(`ID: ${user.id}, Created At: ${user.created_at}`);  
    });
});

addEditListeners();
addDeleteListeners();

}

function addEditListeners(){
userTableBody.querySelectorAll(".editBtn").forEach(button => {
    button.addEventListener("click", (e) => {
    const userId = e.target.getAttribute("data-id");
    const user = users.find(u => u.id == userId);
    if (!user){
        showError("Kullanıcı bulunamadı.");
        return;
    }
    form.firstName.value = user.firstName;
    form.lastName.value = user.lastName;
    form.email.value = user.email;

    form.dataset.editingUserId = userId;

    openForm();
    newUserTitle.textContent = "Kullanıcıyı Düzenle";
    form.querySelector('button[type="submit"]').textContent = "Güncelle";
    });
});
}

function addDeleteListeners(){
userTableBody.querySelectorAll(".deleteBtn").forEach(button => {
    button.addEventListener("click", async (e) => {
    const userId = e.target.getAttribute("data-id");
    if (!confirm("Bu kullanıcıyı silmek istediğinden emin misin?")) return;

    try {
        const response = await fetch(`http://localhost:5000/users/${userId}`, {method:"DELETE"});
        const result = await response.json();

        if(response.ok){
        showSuccess(result.message);
        await fetchUsers();
        } else {
        showError("HATA: " + (result.error || "Bilinmeyen hata"));
        }
    } catch (error){
        showError('İstek sırasında hata oluştu: ' + error.message);
    }
    });
});
}

function openForm(){
formContainer.style.display = 'block';
showFormBtn.style.display = 'none';
}

function closeForm(){
form.reset();
formContainer.style.display = 'none';
showFormBtn.style.display = 'inline-block';
newUserTitle.textContent = "Yeni Kullanıcı Ekle";
form.querySelector('button[type="submit"]').textContent = "Ekle";
delete form.dataset.editingUserId;
}

showFormBtn.addEventListener('click', () => {
openForm();
form.reset();
newUserTitle.textContent = "Yeni Kullanıcı Ekle";
form.querySelector('button[type="submit"]').textContent = "Ekle";
delete form.dataset.editingUserId;
});

document.getElementById('cancelEdit').addEventListener('click', () => {
closeForm();
});

form.addEventListener('submit', async (e) => {
e.preventDefault();


const firstName = form.firstName.value.trim();
const lastName = form.lastName.value.trim();
const email = form.email.value.trim();
const data = { firstName, lastName, email};


const nameRegex = /^[A-Za-zÇçĞğİıÖöŞşÜü]+$/;
if (!nameRegex.test(firstName)|| !nameRegex.test(lastName)) {
    showError("Ad ve soyad sadece harf içermelidir.")
    return;
}

if (firstName.length < 2 || lastName.length < 2){
    showError("Ad ve soyad bir harften uzun olmalıdır.");
    return;
}

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
if (!emailRegex.test(email)) {
    showError("Geçerli bir e-posta adresi girin. Örn: isim@site.com");
    return;
}

const userId = form.dataset.editingUserId;
try {
    let response;
    if (userId){
    response = await fetch(`http://localhost:5000/users/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    } else {
    response = await fetch('http://localhost:5000/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    }

    const result = await response.json();
    if (response.ok) {
    showSuccess(userId ? "Kullanıcı başarıyla güncellendi!" : "Kullanıcı başarıyla eklendi!");
    closeForm();
    await fetchUsers(); 
    } else {
    showError('Hata: ' + (result.error || 'Bilinmeyen hata'));
    }
} catch (err) {
    showError('İstek sırasında hata oluştu: ' + err.message);
}
});

window.onload = fetchUsers;