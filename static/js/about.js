// Efecto fade-in al hacer scroll
document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll(".fade-section");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target); // Para que no se repita
        }
      });
    },
    { threshold: 0.15 } // 15% visible
  );

  sections.forEach((section) => observer.observe(section));
});
