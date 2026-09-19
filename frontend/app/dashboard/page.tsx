"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";


interface User {
  id: number;
  email: string;
  full_name: string;
}


interface School {
  school_id: number;
  school_name: string;
  role: string;
}


export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] =
    useState<User | null>(null);

  const [schools, setSchools] =
    useState<School[]>([]);

  const [loading, setLoading] =
    useState(true);


  useEffect(() => {
    async function load() {
      const token =
        localStorage.getItem("access_token");

      if (!token) {
        router.push("/login");
        return;
      }

      try {
        const headers = {
          Authorization: `Bearer ${token}`,
        };

        const userResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`,
          { headers }
        );

        if (!userResponse.ok) {
          localStorage.removeItem("access_token");
          router.push("/login");
          return;
        }

        const userData =
          await userResponse.json();

        setUser(userData);


        const schoolsResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/schools/mine`,
          { headers }
        );

        const schoolsData =
          await schoolsResponse.json();

        setSchools(schoolsData);

      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);


  function logout() {
    localStorage.removeItem("access_token");
    router.push("/login");
  }


  if (loading) {
    return <p>Загрузка...</p>;
  }


  return (
    <main
      style={{
        maxWidth: 1100,
        margin: "40px auto",
        padding: 20,
      }}
    >
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <h1>SchoolNorm</h1>

          {user && (
            <p>
              {user.full_name}
              <br />
              {user.email}
            </p>
          )}
        </div>

        <button onClick={logout}>
          Выйти
        </button>
      </header>


      <hr />


      <h2>Мои организации</h2>

      {schools.map((school) => (
        <div
          key={school.school_id}
          style={{
            background: "white",
            padding: 20,
            marginBottom: 20,
            borderRadius: 10,
          }}
        >
          <h3>
            {school.school_name}
          </h3>

          <p>
            Роль: <strong>{school.role}</strong>
          </p>
        </div>
      ))}


      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 20,
        }}
      >
        <Card
          title="Нормативные документы"
          text="Федеральные, региональные и ведомственные документы"
        />

        <Card
          title="Изменения"
          text="Новые документы и изменения законодательства"
        />

        <Card
          title="Школьные документы"
          text="Приказы, положения, инструкции и локальные акты"
        />

        <Card
          title="Шаблоны"
          text="Шаблоны документов образовательной организации"
        />
      </div>
    </main>
  );
}


function Card({
  title,
  text,
}: {
  title: string;
  text: string;
}) {
  return (
    <div
      style={{
        background: "white",
        padding: 25,
        borderRadius: 10,
      }}
    >
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}