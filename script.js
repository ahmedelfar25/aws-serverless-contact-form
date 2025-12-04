const API_URL =
  "https://61hcbnlo43.execute-api.us-east-1.amazonaws.com/prod/contact";

const form = document.getElementById("contact-form");
const statusEl = document.getElementById("status");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusEl.textContent = "Sending...";

  const formData = new FormData(form);
  const payload = {
    name: formData.get("name"),
    email: formData.get("email"),
    message: formData.get("message"),
  };

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error("Request failed");
    }

    statusEl.textContent = "Message sent successfully!";
    form.reset();
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Something went wrong. Please try again.";
  }
});
