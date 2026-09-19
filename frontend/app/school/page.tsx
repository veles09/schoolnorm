"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface School {
  id: number;
  name: string;
  short_name: string | null;
  address: string | null;
  region: string | null;
  municipality: string | null;
}

export default function SchoolPage() {
  const router = useRouter();

  const [school, setSchool] = useState<School | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function loadSchool() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        router.push("/login");
        return;
      }

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/schools/my`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          if (response.status === 401) {
            localStorage.removeItem("access_token");
            router.push("/login");
            return;
          }

          throw new Error("Не удалось загрузить данные школы");
        }

        const data = await response.json();
        setSchool(data);
      } catch (error) {
        console.error(error);
        setMessage("Не удалось загрузить данные школы");
      } finally {
        setLoading(false);
      }
    }

    loadSchool();
  }, [router]);

  function updateField(
    field: keyof School,
    value: string
  ) {
    if (!school) return;

    setSchool({
      ...school,
      [field]: value,
    });
  }

  async function saveSchool() {
    if (!school) return;

    const token = localStorage.getItem("access_token");

    if (!token) {
      router.push("/login");
      return;
    }

    setSaving(true);
    setMessage("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/schools/my`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: school.name,
            short_name: school.short_name,
            address: school.address,
            region: school.region,
            municipality: school.municipality,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || "Ошибка сохранения"
        );
      }

      const data = await response.json();

      setSchool(data);
      setMessage("Данные школы сохранены");
    } catch (error) {
      console.error(error);

      setMessage(
        error instanceof Error
          ? error.message
          : "Ошибка сохранения"
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <main style={styles.container}>
        <p>Загрузка...</p>
      </main>
    );
  }

  if (!school) {
    return (
      <main style={styles.container}>
        <h1>Моя школа</h1>
        <p>{message || "Школа не найдена"}</p>

        <button
          onClick={() => router.push("/dashboard")}
          style={styles.secondaryButton}
        >
          Вернуться в кабинет
        </button>
      </main>
    );
  }

  return (
    <main style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={{ marginBottom: 5 }}>
            Моя школа
          </h1>

          <p style={styles.subtitle}>
            Основные сведения об образовательной организации
          </p>
        </div>

        <button
          onClick={() => router.push("/dashboard")}
          style={styles.secondaryButton}
        >
          В кабинет
        </button>
      </div>

      <section style={styles.card}>
        <h2>Основные сведения</h2>

        <div style={styles.form}>
          <label>
            Название школы
            <input
              value={school.name}
              onChange={(e) =>
                updateField("name", e.target.value)
              }
            />
          </label>

          <label>
            Краткое название
            <input
              value={school.short_name ?? ""}
              onChange={(e) =>
                updateField(
                  "short_name",
                  e.target.value
                )
              }
              placeholder="Например: Школа №1"
            />
          </label>

          <label>
            Адрес
            <input
              value={school.address ?? ""}
              onChange={(e) =>
                updateField(
                  "address",
                  e.target.value
                )
              }
              placeholder="Адрес образовательной организации"
            />
          </label>

          <label>
            Регион
            <input
              value={school.region ?? ""}
              onChange={(e) =>
                updateField(
                  "region",
                  e.target.value
                )
              }
              placeholder="Например: Московская область"
            />
          </label>

          <label>
            Муниципалитет
            <input
              value={school.municipality ?? ""}
              onChange={(e) =>
                updateField(
                  "municipality",
                  e.target.value
                )
              }
              placeholder="Например: городской округ"
            />
          </label>
        </div>

        <div style={styles.actions}>
          <button
            onClick={saveSchool}
            disabled={saving}
            style={styles.primaryButton}
          >
            {saving ? "Сохранение..." : "Сохранить"}
          </button>

          {message && (
            <span style={styles.message}>
              {message}
            </span>
          )}
        </div>
      </section>
    </main>
  );
}

const styles = {
  container: {
    maxWidth: 1000,
    margin: "40px auto",
    padding: 20,
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 30,
  },

  subtitle: {
    color: "#666",
  },

  card: {
    background: "white",
    padding: 30,
    borderRadius: 12,
    boxShadow: "0 2px 10px rgba(0,0,0,0.05)",
  },

  form: {
    display: "grid",
    gap: 20,
    marginTop: 25,
  },

  actions: {
    display: "flex",
    alignItems: "center",
    gap: 20,
    marginTop: 30,
  },

  message: {
    color: "#444",
  },

  primaryButton: {
    padding: "10px 20px",
    border: "none",
    borderRadius: 8,
    cursor: "pointer",
  },

  secondaryButton: {
    padding: "10px 20px",
    border: "1px solid #ccc",
    borderRadius: 8,
    background: "white",
    cursor: "pointer",
  },
};