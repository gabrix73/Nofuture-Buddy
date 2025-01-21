document.addEventListener("DOMContentLoaded", () => {
  // Seleziona gli elementi dalla DOM
  const showKeyboardButton = document.getElementById("showKeyboardButton");
  const keyboardTooltip = document.getElementById("keyboardTooltip");
  const keyboardContainer = document.getElementById("keyboardContainer");
  const closeKeyboardButton = document.getElementById("closeKeyboardButton");
  const virtualKeyboard = document.getElementById("virtualKeyboard");
  const keyboardHeader = document.getElementById("keyboardHeader");
  const textInput = document.getElementById("textInput"); // Assicurati che textInput sia definito qui

  console.log("Keyboard elements loaded:", {
    showKeyboardButton,
    keyboardTooltip,
    keyboardContainer,
    closeKeyboardButton,
    virtualKeyboard,
    keyboardHeader,
    textInput
  }); // Aggiungi un log per il debug

  // Caratteri della tastiera
  const letters = "abcdefghijklmnopqrstuvwxyz".split("");
  const numbers = "0123456789".split("");
  const symbols = "+-=.,/,*".split("");

  // Mostra il popup al passaggio del mouse
  showKeyboardButton.addEventListener("mouseenter", () => {
    keyboardTooltip.style.display = "block";
    keyboardTooltip.style.top = `${showKeyboardButton.offsetTop - keyboardTooltip.offsetHeight - 10}px`; // Posiziona il popup in alto
  });

  // Nasconde il popup quando il mouse esce
  showKeyboardButton.addEventListener("mouseleave", () => {
    keyboardTooltip.style.display = "none";
  });

  // Mostra la tastiera virtuale al clic sul pulsante
  showKeyboardButton.addEventListener("click", () => {
    keyboardContainer.style.display = "block"; // Mostra la tastiera
    generateKeyboard(textInput); // Genera i tasti della tastiera
  });

  // Nasconde la tastiera virtuale al clic su "Close"
  closeKeyboardButton.addEventListener("click", () => {
    keyboardContainer.style.display = "none"; // Nasconde la tastiera
  });

  // Genera i tasti della tastiera virtuale
  function generateKeyboard(textInput) {
    virtualKeyboard.innerHTML = ""; // Pulisce il contenitore della tastiera

    // Mescola i tasti delle lettere
    const shuffledLetters = letters.sort(() => Math.random() - 0.5);
    // Mescola i tasti dei numeri
    const shuffledNumbers = numbers.sort(() => Math.random() - 0.5);
    // Mescola i tasti dei simboli
    const shuffledSymbols = symbols.sort(() => Math.random() - 0.5);

    // Aggiunge i tasti delle lettere
    shuffledLetters.forEach((key) => {
      const keyElement = document.createElement("div");
      keyElement.classList.add("key");
      keyElement.textContent = key;

      // Aggiunge un evento al clic
      keyElement.addEventListener("click", () => {
        showPopup(keyElement, key, key.toUpperCase());
      });

      virtualKeyboard.appendChild(keyElement);
    });

    // Aggiunge i tasti dei numeri
    shuffledNumbers.forEach((key) => {
      const keyElement = document.createElement("div");
      keyElement.classList.add("key");
      keyElement.textContent = key;

      // Aggiunge un evento al clic
      keyElement.addEventListener("click", () => {
        showPopup(keyElement, key, getSymbolsForNumber(key));
      });

      virtualKeyboard.appendChild(keyElement);
    });

    // Aggiunge i tasti dei simboli
    shuffledSymbols.forEach((key) => {
      const keyElement = document.createElement("div");
      keyElement.classList.add("key");
      keyElement.textContent = key;

      // Aggiunge un evento al clic
      keyElement.addEventListener("click", () => {
        textInput.value += key; // Inserisce il carattere nella textarea
      });

      virtualKeyboard.appendChild(keyElement);
    });

    // Aggiunge i tasti speciali (es. Spazio e Cancella)
    addSpecialKeys(textInput);
  }

  // Aggiunge i tasti "Spazio" e "Cancella"
  function addSpecialKeys(textInput) {
    // Tasto Spazio
    const spaceKey = document.createElement("div");
    spaceKey.classList.add("key");
    spaceKey.textContent = "Space";
    spaceKey.addEventListener("click", () => {
      textInput.value += " ";
    });
    virtualKeyboard.appendChild(spaceKey);

    // Tasto Backspace
    const backspaceKey = document.createElement("div");
    backspaceKey.classList.add("key");
    backspaceKey.textContent = "Backspace";
    backspaceKey.addEventListener("click", () => {
      textInput.value = textInput.value.slice(0, -1); // Rimuove l'ultimo carattere
    });
    virtualKeyboard.appendChild(backspaceKey);
  }

  // Mostra il popup per le maiuscole o i simboli
  function showPopup(keyElement, key, options) {
    const popup = document.createElement("div");
    popup.classList.add("popup");
    popup.style.position = "absolute";
    popup.style.top = `${keyElement.offsetTop + keyElement.offsetHeight}px`;
    popup.style.left = `${keyElement.offsetLeft}px`;

    options.forEach(option => {
      const optionElement = document.createElement("div");
      optionElement.classList.add("popup-option");
      optionElement.textContent = option;
      optionElement.addEventListener("click", () => {
        textInput.value += option;
        popup.remove();
      });
      popup.appendChild(optionElement);
    });

    document.body.appendChild(popup);
  }

  // Ottiene i simboli corrispondenti per un numero
  function getSymbolsForNumber(number) {
    const symbolMap = {
      "0": ["=", "+", "-"],
      "1": ["!", "@", "#"],
      "2": ["$", "%", "^"],
      "3": ["&", "*", "("],
      "4": [")", "_", "="],
      "5": ["{", "}", "["],
      "6": ["]", ":", ";"],
      "7": ["'", '"', "\\"],
      "8": ["|", "<", ">"],
      "9": ["?", "/", "`"]
    };
    return symbolMap[number] || [];
  }

  // Elementi per il trascinamento
  let isDragging = false;
  let offsetX = 0, offsetY = 0;

  // Avvia il trascinamento quando si clicca sull'intestazione
  keyboardHeader.addEventListener("mousedown", (e) => {
    isDragging = true;
    offsetX = e.clientX - keyboardContainer.offsetLeft;
    offsetY = e.clientY - keyboardContainer.offsetTop;
  });

  // Sposta la tastiera durante il trascinamento
  document.addEventListener("mousemove", (e) => {
    if (isDragging) {
      keyboardContainer.style.left = `${e.clientX - offsetX}px`;
      keyboardContainer.style.top = `${e.clientY - offsetY}px`;
    }
  });

  // Termina il trascinamento quando si rilascia il mouse
  document.addEventListener("mouseup", () => {
    isDragging = false;
  });
});
