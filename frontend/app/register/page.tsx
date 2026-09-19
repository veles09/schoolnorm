"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";


export default function RegisterPage() {
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [schoolName, setSchoolName] = useState("");
  const [error, setError] = useState("");


  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    setError("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            full_name: fullName,
            email,
            password,
            school_name: schoolName,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Ошибка регистрации"
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
          : "Ошибка регистрации"
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
      <h1>Регистрация</h1>

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
          placeholder="ФИО"
          value={fullName}
          onChange={(e) =>
            setFullName(e.target.value)
          }
        />

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

        <input
          placeholder="Название образовательной организации"
          value={schoolName}
          onChange={(e) =>
            setSchoolName(e.target.value)
          }
        />

        <button type="submit">
          Зарегистрироваться
        </button>
      </form>

      <p>
        Уже есть аккаунт?{" "}
        <a href="/login">Войти</a>
      </p>
    </main>
  );
}