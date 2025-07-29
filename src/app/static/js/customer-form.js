// Customer form enhancements
class CustomerForm {
  constructor() {
    this.form = document.querySelector("form");
    this.nameInput = document.getElementById("name");
    this.phoneInput = document.getElementById("phone");
    this.similarDiv = document.getElementById("similar-customers");

    this.init();
  }

  init() {
    // Auto-search for similar customers while typing name
    if (this.nameInput) {
      this.nameInput.addEventListener(
        "input",
        this.debounce(this.searchSimilar.bind(this), 500),
      );
    }

    // Format phone numbers as they type
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach((input) => {
      input.addEventListener("input", this.formatPhone.bind(this));
    });

    // Form validation
    if (this.form) {
      this.form.addEventListener("submit", this.validateForm.bind(this));
    }
  }

  async searchSimilar(event) {
    const query = event.target.value.trim();

    if (query.length < 3) {
      this.similarDiv.classList.add("hidden");
      return;
    }

    try {
      const response = await fetch(
        `/api/v1/customers/search?q=${encodeURIComponent(query)}&limit=5`,
      );
      const data = await response.json();

      if (data.results && data.results.length > 0) {
        this.showSimilarCustomers(data.results);
      } else {
        this.similarDiv.classList.add("hidden");
      }
    } catch (error) {
      console.error("Search error:", error);
    }
  }

  showSimilarCustomers(customers) {
    const listDiv = document.getElementById("similar-list");

    listDiv.innerHTML = customers
      .map(
        (customer) => `
            <div class="mt-2 flex items-center justify-between">
                <div>
                    <span class="font-medium">${customer.name}</span>
                    <span class="text-gray-500 ml-2">${customer.phone}</span>
                    ${
                      customer.phone_secondary
                        ? `<span class="text-gray-400 ml-1">/ ${customer.phone_secondary}</span>`
                        : ""
                    }
                </div>
                <a href="/customers/${
                  customer.id
                }" class="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                    View →
                </a>
            </div>
        `,
      )
      .join("");

    this.similarDiv.classList.remove("hidden");
  }

  formatPhone(event) {
    // Basic phone formatting (can be enhanced)
    let value = event.target.value.replace(/\D/g, "");

    // Don't format if user is typing international format
    if (event.target.value.startsWith("+")) {
      return;
    }

    // Simple formatting for 10-digit numbers
    if (value.length === 10) {
      value = value.replace(/(\d{3})(\d{3})(\d{4})/, "($1) $2-$3");
      event.target.value = value;
    }
  }

  validateForm(event) {
    // Clear previous errors
    document.querySelectorAll(".field-error").forEach((el) => el.remove());

    let valid = true;

    // Validate name
    if (!this.nameInput.value.trim()) {
      this.showFieldError(this.nameInput, "Name is required");
      valid = false;
    }

    // Validate phone
    const phone = this.phoneInput.value.replace(/\D/g, "");
    if (phone.length < 7) {
      this.showFieldError(this.phoneInput, "Please enter a valid phone number");
      valid = false;
    }

    // Validate email if provided
    const emailInput = document.getElementById("email");
    if (emailInput.value && !this.isValidEmail(emailInput.value)) {
      this.showFieldError(emailInput, "Please enter a valid email address");
      valid = false;
    }

    if (!valid) {
      event.preventDefault();
    }
  }

  showFieldError(field, message) {
    const error = document.createElement("p");
    error.className = "field-error mt-1 text-sm text-red-600";
    error.textContent = message;
    field.parentElement.appendChild(error);
    field.focus();
    field.classList.add("border-red-300");
  }

  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  // Only initialize if we're on a customer form page
  if (document.querySelector('.customer-form, form[action*="/customers/"]')) {
    new CustomerForm();
  }
});
