var password = document.querySelector(".password");
var li_long = document.querySelector(".validation ul li:nth-child(1)");
var li_uppercase = document.querySelector(".validation ul li:nth-child(2)");
var li_symbols = document.querySelector(".validation ul li:nth-child(3)");
var li_numbers = document.querySelector(".validation ul li:nth-child(4)");
var line_long = li_long.querySelector(".line");
var li_num = li_long.querySelector("i");
var generateBtn = document.getElementById("generate-password");
var strengthValue = document.getElementById("strength-value");
var strengthMeterFill = document.querySelector(".strength-meter-fill");

// Функция генерации случайного надежного пароля
function generatePassword() {
    const length = 12; // Длина пароля
    const uppercaseChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ";
    const lowercaseChars = "abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя";
    const numberChars = "0123456789";
    const specialChars = "!@$%^&*";
    
    // Гарантируем наличие всех типов символов
    let result = '';
    result += uppercaseChars.charAt(Math.floor(Math.random() * uppercaseChars.length));
    result += lowercaseChars.charAt(Math.floor(Math.random() * lowercaseChars.length));
    result += numberChars.charAt(Math.floor(Math.random() * numberChars.length));
    result += specialChars.charAt(Math.floor(Math.random() * specialChars.length));
    
    // Добавляем оставшиеся символы
    const allChars = uppercaseChars + lowercaseChars + numberChars + specialChars;
    for (let i = result.length; i < length; i++) {
        result += allChars.charAt(Math.floor(Math.random() * allChars.length));
    }
    
    // Перемешиваем символы в пароле
    result = result.split('').sort(() => Math.random() - 0.5).join('');
    
    return result;
}

// Обработчик клика по кнопке
generateBtn.addEventListener('click', function() {
    password.value = generatePassword();
    checkPassword();
    
    // Добавляем небольшую анимацию при генерации
    this.style.transform = 'scale(0.97)';
    setTimeout(() => {
        this.style.transform = 'scale(1)';
    }, 150);
});

checkPassword();
password.onkeyup= function(){
    checkPassword();
}

// Функция для расчета общей надежности пароля
function calculatePasswordStrength(password) {
    let score = 0;
    
    // Длина пароля (максимум 40 баллов)
    if (password.length >= 12) {
        score += 40;
    } else if (password.length > 0) {
        score += Math.floor(password.length * 3.33); // 3.33 * 12 = ~40
    }
    
    // Наличие заглавных букв (20 баллов)
    if (/[A-ZА-ЯЁ]/u.test(password)) {
        score += 20;
    }
    
    // Наличие цифр (20 баллов)
    if (/\d/.test(password)) {
        score += 20;
    }
    
    // Наличие спецсимволов (20 баллов)
    if (/[!@$%^&*]/.test(password)) {
        score += 20;
    }
    
    return Math.min(score, 100); // Максимум 100%
}

function checkPassword(){
    var uppercase = /^(?=.*[A-ZА-ЯЁ])/u;
    var numbers = new RegExp('(?=.*[0-9])');
    var symbols = new RegExp('(?=.*[!@\$%\^&\*])');
    
    // Проверяем критерии
    if(uppercase.test(password.value)){
        li_uppercase.classList.add("valid");
    }
    else{
        li_uppercase.classList.remove("valid");
    }
    if(numbers.test(password.value)){
        li_numbers.classList.add("valid");
    }
    else{
        li_numbers.classList.remove("valid");
    }
    if(symbols.test(password.value)){
        li_symbols.classList.add("valid");
    }
    else{
        li_symbols.classList.remove("valid");
    }
    
    // Обновляем индикатор длины
    if(password.value.length == 0){
        line_long.style.width = "15px";
        li_num.innerHTML = "0";
        line_long.style.background = "#da00ff";
        line_long.style.boxShadow = "0 0 4px #da00ff";
    }
    else if(password.value.length < 12){
        line_long.style.width = (password.value.length / 12 * 100) + "%";
        li_num.innerHTML = password.value.length;
        line_long.style.background = "#da00ff";
        line_long.style.boxShadow = "0 0 4px #da00ff";
    }
    else{
        line_long.style.width = "100%";
        li_num.innerHTML = password.value.length;
        line_long.style.background = "#00eeff";
        line_long.style.boxShadow = "0 0 10px #00eeff";
    }
    
    // Обновляем общую оценку надежности
    const strength = calculatePasswordStrength(password.value);
    strengthValue.textContent = strength + "%";
    strengthMeterFill.style.width = strength + "%";
    
    // Меняем цвет оценки в зависимости от надежности
    if (strength < 40) {
        strengthValue.style.color = "#da00ff";
        strengthValue.style.textShadow = "0 0 3px #da00ff";
    } else if (strength < 70) {
        strengthValue.style.color = "#da00ff";
        strengthValue.style.textShadow = "0 0 3px #da00ff";
    } else {
        strengthValue.style.color = "#00eeff";
        strengthValue.style.textShadow = "0 0 3px #00eeff";
    }
}