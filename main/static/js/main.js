// Инициализация Lucide иконок
document.addEventListener("DOMContentLoaded", () => {
  const lucide = window.lucide // Declare the lucide variable
  if (typeof lucide !== "undefined") {
    lucide.createIcons()
  }
})

// Утилиты для работы с API
class API {
  static async request(url, options = {}) {
    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": this.getCSRFToken(),
      },
      credentials: "same-origin",
    }

    const response = await fetch(url, { ...defaultOptions, ...options })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  static getCSRFToken() {
    const cookies = document.cookie.split(";")
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split("=")
      if (name === "csrftoken") {
        return value
      }
    }
    return ""
  }

  static async get(url) {
    return this.request(url, { method: "GET" })
  }

  static async post(url, data) {
    return this.request(url, {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  static async put(url, data) {
    return this.request(url, {
      method: "PUT",
      body: JSON.stringify(data),
    })
  }

  static async delete(url) {
    return this.request(url, { method: "DELETE" })
  }
}

// Утилиты для уведомлений
class Notifications {
  static show(message, type = "info") {
    const container = this.getContainer()
    const notification = this.create(message, type)

    container.appendChild(notification)

    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
      this.remove(notification)
    }, 5000)
  }

  static getContainer() {
    let container = document.querySelector(".notifications-container")
    if (!container) {
      container = document.createElement("div")
      container.className = "notifications-container"
      container.style.cssText = `
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            `
      document.body.appendChild(container)
    }
    return container
  }

  static create(message, type) {
    const notification = document.createElement("div")
    notification.className = `alert alert-${type}`
    notification.style.cssText = `
            min-width: 300px;
            box-shadow: var(--shadow-lg);
            animation: slideIn 0.3s ease-out;
        `

    const icon = this.getIcon(type)
    notification.innerHTML = `
            <i data-lucide="${icon}"></i>
            <span>${message}</span>
            <button class="btn-icon" onclick="this.parentElement.remove()">
                <i data-lucide="x"></i>
            </button>
        `

    // Инициализация иконок
    const lucide = window.lucide // Declare the lucide variable
    if (typeof lucide !== "undefined") {
      lucide.createIcons()
    }

    return notification
  }

  static getIcon(type) {
    const icons = {
      success: "check-circle",
      error: "alert-circle",
      warning: "alert-triangle",
      info: "info",
    }
    return icons[type] || "info"
  }

  static remove(notification) {
    notification.style.animation = "slideOut 0.3s ease-in"
    setTimeout(() => {
      if (notification.parentElement) {
        notification.parentElement.removeChild(notification)
      }
    }, 300)
  }

  static success(message) {
    this.show(message, "success")
  }

  static error(message) {
    this.show(message, "error")
  }

  static warning(message) {
    this.show(message, "warning")
  }

  static info(message) {
    this.show(message, "info")
  }
}

// Добавляем CSS анимации
const style = document.createElement("style")
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`
document.head.appendChild(style)

// Утилиты для модальных окон
class Modal {
  static show(content, title = "") {
    const modal = this.create(content, title)
    document.body.appendChild(modal)

    // Фокус на модальном окне
    modal.focus()

    return modal
  }

  static create(content, title) {
    const modal = document.createElement("div")
    modal.className = "modal-overlay"
    modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            animation: fadeIn 0.2s ease-out;
        `

    modal.innerHTML = `
            <div class="modal-content" style="
                background: var(--surface);
                border-radius: var(--radius);
                box-shadow: var(--shadow-lg);
                max-width: 500px;
                width: 90%;
                max-height: 90vh;
                overflow-y: auto;
                animation: scaleIn 0.2s ease-out;
            ">
                ${
                  title
                    ? `
                    <div class="modal-header" style="
                        padding: 1.5rem;
                        border-bottom: 1px solid var(--border);
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                    ">
                        <h3 style="font-size: 1.125rem; font-weight: 600;">${title}</h3>
                        <button class="btn-icon modal-close">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                `
                    : ""
                }
                <div class="modal-body" style="padding: 1.5rem;">
                    ${content}
                </div>
            </div>
        `

    // Закрытие по клику на overlay
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        this.close(modal)
      }
    })

    // Закрытие по кнопке
    const closeBtn = modal.querySelector(".modal-close")
    if (closeBtn) {
      closeBtn.addEventListener("click", () => this.close(modal))
    }

    // Закрытие по Escape
    const handleEscape = (e) => {
      if (e.key === "Escape") {
        this.close(modal)
        document.removeEventListener("keydown", handleEscape)
      }
    }
    document.addEventListener("keydown", handleEscape)

    // Инициализация иконок
    const lucide = window.lucide // Declare the lucide variable
    if (typeof lucide !== "undefined") {
      lucide.createIcons()
    }

    return modal
  }

  static close(modal) {
    modal.style.animation = "fadeOut 0.2s ease-in"
    setTimeout(() => {
      if (modal.parentElement) {
        modal.parentElement.removeChild(modal)
      }
    }, 200)
  }
}

// Добавляем CSS для модальных окон
const modalStyle = document.createElement("style")
modalStyle.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    @keyframes scaleIn {
        from {
            transform: scale(0.9);
            opacity: 0;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }
`
document.head.appendChild(modalStyle)

// Утилиты для форм
class Forms {
  static serialize(form) {
    const formData = new FormData(form)
    const data = {}

    for (const [key, value] of formData.entries()) {
      data[key] = value
    }

    return data
  }

  static validate(form) {
    const inputs = form.querySelectorAll("input[required], textarea[required], select[required]")
    let isValid = true

    inputs.forEach((input) => {
      if (!input.value.trim()) {
        this.showFieldError(input, "Это поле обязательно для заполнения")
        isValid = false
      } else {
        this.clearFieldError(input)
      }
    })

    return isValid
  }

  static showFieldError(field, message) {
    this.clearFieldError(field)

    const error = document.createElement("div")
    error.className = "field-error"
    error.style.cssText = `
            color: var(--error);
            font-size: 0.75rem;
            margin-top: 0.25rem;
        `
    error.textContent = message

    field.style.borderColor = "var(--error)"
    field.parentElement.appendChild(error)
  }

  static clearFieldError(field) {
    const error = field.parentElement.querySelector(".field-error")
    if (error) {
      error.remove()
    }
    field.style.borderColor = ""
  }

  static reset(form) {
    form.reset()
    const errors = form.querySelectorAll(".field-error")
    errors.forEach((error) => error.remove())

    const fields = form.querySelectorAll("input, textarea, select")
    fields.forEach((field) => {
      field.style.borderColor = ""
    })
  }
}

// Глобальные утилиты
window.API = API
window.Notifications = Notifications
window.Modal = Modal
window.Forms = Forms
