export const metadata = {
  title: "SchoolNorm",
  description:
    "Нормативное сопровождение образовательных организаций",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body
        style={{
          margin: 0,
          fontFamily: "Arial, sans-serif",
          background: "#f5f6f8",
        }}
      >
        {children}
      </body>
    </html>
  );
}