"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";


export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");


  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    setError("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Ошибка входа"
        );
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      router.push("/dashboard");

    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Ошибка входа"
      );
    }
  }


  return (
    <main
      style={{
        maxWidth: 500,
        margin: "60px auto",
        padding: 20,
      }}
    >
      <h1>Вход</h1>

      {error && (
        <p style={{ color: "red" }}>
          {error}
        </p>
      )}

      <form
        onSubmit={handleSubmit}
        style={{
          display: "grid",
          gap: 15,
        }}
      >
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <button type="submit">
          Войти
        </button>
      </form>

      <p>
        Нет аккаунта?{" "}
        <a href="/register">
          Зарегистрироваться
        </a>
      </p>
    </main>
  );
}