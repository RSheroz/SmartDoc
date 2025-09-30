
// Функциональность страницы документов
document.addEventListener("DOMContentLoaded", () => {
  // ===== Получаем элементы из DOM =====
  const searchInput = document.getElementById("search-query")
  const statusFilter = document.getElementById("filter-status")
  const templateFilter = document.getElementById("filter-template")
  const resetButton = document.getElementById("reset-filters")
  const documentsContainer = document.getElementById("documents-list") // сама таблица
  const tbody = documentsContainer.querySelector("tbody")

  // ===== API =====
  const API = {
    get: async (url) => {
      const response = await fetch(url)
      if (!response.ok) throw new Error("Network response was not ok")
      return response.json()
    },
    getCSRFToken: () => {
      const name = "csrftoken"
      const cookies = document.cookie.split(";")
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim()
        if (cookie.substring(0, name.length + 1) === name + "=") {
          return decodeURIComponent(cookie.substring(name.length + 1))
        }
      }
      return ""
    },
  }

  // ===== Modal =====
  const Modal = {
    show: (content, title) => {
      const modalOverlay = document.createElement("div")
      modalOverlay.className = "modal-overlay"
      modalOverlay.innerHTML = `
        <style>
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        .modal {
          background: #fff;
          border-radius: 12px;
          padding: 1rem;
          width: 600px;
          max-width: 90%;
          box-shadow: 0 10px 25px rgba(0,0,0,0.2);
          animation: fadeIn 0.3s ease;
        }
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid #eee;
          padding-bottom: 0.5rem;
          margin-bottom: 1rem;
        }
        .modal-body {
          max-height: 70vh;
          overflow-y: auto;
          line-height: 1.6;
        }
        .btn-icon {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 1.2rem;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        </style>
        <div class="modal">
          <div class="modal-header">
            <h3>${title}</h3>
            <button class="btn-icon" title="Закрыть" onclick="this.closest('.modal-overlay').remove()">
              <i data-lucide="x">X</i>
            </button>
          </div>
          <div class="modal-body">${content}</div>
        </div>
      `
      document.body.appendChild(modalOverlay)
      return modalOverlay
    },
  }

  // ===== Notifications =====
  const Notifications = {
    error: (message) => alert(message),
  }

  // ===== Фильтрация документов =====
  function filterDocuments() {
    const searchQuery = searchInput.value.toLowerCase().trim()
    const statusValue = statusFilter.value
    const templateValue = templateFilter.value

    const rows = tbody.querySelectorAll("tr[data-id]")
    let visibleCount = 0

    rows.forEach((row) => {
      let isVisible = true

      const title = (row.dataset.title || "").toLowerCase()
      const content = (row.dataset.content || "").toLowerCase()

      if (searchQuery && !title.includes(searchQuery) && !content.includes(searchQuery)) {
        isVisible = false
      }

      if (statusValue !== "all" && row.dataset.status !== statusValue) {
        isVisible = false
      }

      if (templateValue !== "all" && row.dataset.template !== templateValue) {
        isVisible = false
      }

      row.style.display = isVisible ? "" : "none"
      if (isVisible) visibleCount++
    })
    if (visibleCount === 0) {showEmptyState(true)}
    else{showEmptyState(false)}
  }
  // ===== Сброс фильтров =====
  function resetFilters() {
    searchInput.value = ""
    statusFilter.value = "all"
    templateFilter.value = "all"
    filterDocuments()
  }
 function showEmptyState(show) {
    let emptyState = documentsContainer.querySelector(".empty-state")

    if (show && !emptyState) {
      emptyState = document.createElement("div")
      emptyState.className = "empty-state"
      emptyState.innerHTML = `
                <i data-lucide="search"></i>
                <h3>Документы не найдены</h3>
                <p>Попробуйте изменить параметры поиска или фильтры</p>
                <button class="btn btn-outline reset-btn">Сбросить фильтры</button>
            `
      documentsContainer.appendChild(emptyState)
      const resetBtn = emptyState.querySelector(".reset-btn")
      resetBtn.addEventListener("click", resetFilters)
      if (typeof lucide !== "undefined") {
        lucide.createIcons()
      }
    } else if (!show && emptyState) {
      emptyState.remove()
    }
  }

  // ===== Слушатели =====
  searchInput.addEventListener("input", filterDocuments)
  statusFilter.addEventListener("change", filterDocuments)
  templateFilter.addEventListener("change", filterDocuments)
  resetButton.addEventListener("click", resetFilters)

  // ===== Просмотр документа =====
  tbody.addEventListener("click", async (e) => {
    const button = e.target.closest(".btn-icon")
    if (!button) return
    const row = button.closest("tr[data-id]")
    if (!row) return
    const documentId = row.dataset.id
    const action = button.title.toLowerCase()

    if (action === "просмотр") {
      try {
        const document = await API.get(`/api/documents/${documentId}/`)
        const content = `
          <h4>${document.title}</h4>
          <div class="document-meta" style="margin:1rem 0; padding:1rem; background:#f9f9f9; border-radius:8px;">
            <p><strong>Автор:</strong> ${document.created_by_name}</p>
            <p><strong>Статус:</strong> ${document.status_display}</p>
            <p><strong>Создан:</strong> ${new Date(document.created_at).toLocaleString("ru-RU")}</p>
            ${document.recipient_name ? `<p><strong>Получатель:</strong> ${document.recipient_name}</p>` : ""}
          </div>
          <div class="document-content" style="white-space: pre-wrap; line-height: 1.6;">
            ${document.content}
          </div>
        `
        Modal.show(content, "Просмотр документа")
      } catch (err) {
        Notifications.error(`Ошибка при загрузке документа ${documentId}`)
      }
    }
  })

  // ===== Запуск при загрузке =====
  filterDocuments()
})

