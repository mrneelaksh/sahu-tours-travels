document.addEventListener("DOMContentLoaded", () => {
  const loader = document.querySelector(".loader");
  setTimeout(() => loader && loader.classList.add("hide"), 500);

  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("show"); });
  }, {threshold: .12});
  document.querySelectorAll(".reveal").forEach(el => obs.observe(el));

  document.querySelectorAll(".flash").forEach(el => setTimeout(() => el.remove(), 5000));

  document.addEventListener("mousemove", e => {
    const c = document.querySelector(".cursor"), d = document.querySelector(".cursor-dot");
    if(c){ c.style.transform=`translate(${e.clientX}px,${e.clientY}px)`; }
    if(d){ d.style.transform=`translate(${e.clientX}px,${e.clientY}px)`; }
  });
});