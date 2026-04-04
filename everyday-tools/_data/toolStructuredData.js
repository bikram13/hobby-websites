const BASE = "https://everyday-tools.pages.dev";

function webApp(name, url, description) {
  return {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": name,
    "url": url,
    "description": description,
    "applicationCategory": "UtilityApplication",
    "operatingSystem": "Any",
    "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" }
  };
}

function breadcrumbs(items) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, i) => ({
      "@type": "ListItem",
      "position": i + 1,
      "name": item.name,
      "item": item.url
    }))
  };
}

function ld(categorySlug, categoryName, toolSlug, toolName, description) {
  const toolUrl = `${BASE}/${categorySlug}/${toolSlug}/`;
  const catUrl = `${BASE}/${categorySlug}/`;
  return JSON.stringify([
    webApp(toolName, toolUrl, description),
    breadcrumbs([
      { name: "Home", url: `${BASE}/` },
      { name: categoryName, url: catUrl },
      { name: toolName, url: toolUrl }
    ])
  ]);
}

module.exports = {
  // Finance
  "tip-calculator": ld("finance", "Finance Tools", "tip-calculator", "Tip Calculator", "Calculate tip amounts and split the bill between friends."),
  "percentage-calculator": ld("finance", "Finance Tools", "percentage-calculator", "Percentage Calculator", "Calculate percentages three ways: X% of Y, X is what % of Y, and percentage change."),
  "loan-calculator": ld("finance", "Finance Tools", "loan-calculator", "Loan / EMI Calculator", "Calculate monthly loan payments using the standard amortization formula."),
  // Health
  "bmi-calculator": ld("health", "Health Tools", "bmi-calculator", "BMI Calculator", "Calculate your Body Mass Index from height and weight in metric or imperial units."),
  "age-calculator": ld("health", "Health Tools", "age-calculator", "Age Calculator", "Calculate your exact age in years, months, and days from your date of birth."),
  // Unit Converters
  "unit-converter": ld("unit-converters", "Unit Converters", "unit-converter", "Unit Converter", "Convert length, weight, temperature, and volume between metric and imperial units."),
  // Utility
  "time-zone-converter": ld("utility", "Utility Tools", "time-zone-converter", "Time Zone Converter", "Convert times between major world time zones instantly."),
  "password-generator": ld("utility", "Utility Tools", "password-generator", "Password Generator", "Generate secure random passwords with configurable length and character types."),
  "random-number-generator": ld("utility", "Utility Tools", "random-number-generator", "Random Number Generator", "Generate a random integer within any minimum and maximum range you specify."),
};
