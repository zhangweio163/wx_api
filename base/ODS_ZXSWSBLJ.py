# python
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from base.datacenter_mind_mysql_connector import DataCenterMindMySQLConnector


@dataclass
class ODS_ZXSWSBLJ:
    ZYGCXX010101: str  # 主键
    JCXX010101: str
    ZYGFW020101: str
    ZYGFW020102: str
    ZYGFW020103: str
    ZYGFW020104: str
    ZYGFW020105: Optional[str] = None
    GZFW040208: Optional[str] = None
    ZYGCXX01018: str = ""

    TABLE_NAME = "ODS_ZXSWSBLJ"
    PK = "ZYGCXX010101"

    def insert(self, db: Optional[DataCenterMindMySQLConnector] = None) -> bool:
        connector = db or DataCenterMindMySQLConnector()
        if connector.connection is None:
            connector.connect()
        sql = (
            f"INSERT INTO {self.TABLE_NAME} "
            "(ZYGCXX010101, JCXX010101, ZYGFW020101, ZYGFW020102, ZYGFW020103, "
            "ZYGFW020104, ZYGFW020105, GZFW040208, ZYGCXX01018) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        )
        values = (
            self.ZYGCXX010101,
            self.JCXX010101,
            self.ZYGFW020101,
            self.ZYGFW020102,
            self.ZYGFW020103,
            self.ZYGFW020104,
            self.ZYGFW020105,
            self.GZFW040208,
            self.ZYGCXX01018,
        )
        try:
            with connector.connection.cursor() as cursor:
                cursor.execute(sql, values)
            connector.connection.commit()
            return True
        except Exception as e:
            print(f"Insert failed: {e}")
            connector.connection.rollback()
            return False

    def update(self, db: Optional[DataCenterMindMySQLConnector] = None, fields: Optional[List[str]] = None) -> bool:
        connector = db or DataCenterMindMySQLConnector()
        if connector.connection is None:
            connector.connect()
        # 默认更新除主键外的所有字段；也可通过`fields`指定更新字段名列表
        all_fields = [
            "JCXX010101",
            "ZYGFW020101",
            "ZYGFW020102",
            "ZYGFW020103",
            "ZYGFW020104",
            "ZYGFW020105",
            "GZFW040208",
            "ZYGCXX01018",
        ]
        update_fields = fields if fields else all_fields
        set_parts = [f"{f}=%s" for f in update_fields]
        sql = f"UPDATE {self.TABLE_NAME} SET {', '.join(set_parts)} WHERE {self.PK}=%s"
        values = [getattr(self, f) for f in update_fields] + [self.ZYGCXX010101]
        try:
            with connector.connection.cursor() as cursor:
                cursor.execute(sql, values)
            connector.connection.commit()
            return True
        except Exception as e:
            print(f"Update failed: {e}")
            connector.connection.rollback()
            return False

    @classmethod
    def delete_by_pk(cls, pk: str, db: Optional[DataCenterMindMySQLConnector] = None) -> bool:
        connector = db or DataCenterMindMySQLConnector()
        if connector.connection is None:
            connector.connect()
        sql = f"DELETE FROM {cls.TABLE_NAME} WHERE {cls.PK}=%s"
        try:
            with connector.connection.cursor() as cursor:
                cursor.execute(sql, (pk,))
            connector.connection.commit()
            return True
        except Exception as e:
            print(f"Delete failed: {e}")
            connector.connection.rollback()
            return False

    @classmethod
    def get_by_pk(cls, pk: str, db: Optional[DataCenterMindMySQLConnector] = None) -> Optional["ODS_ZXSWSBLJ"]:
        connector = db or DataCenterMindMySQLConnector()
        if connector.connection is None:
            connector.connect()
        sql = f"SELECT * FROM {cls.TABLE_NAME} WHERE {cls.PK}=%s LIMIT 1"
        try:
            with connector.connection.cursor() as cursor:
                cursor.execute(sql, (pk,))
                row: Optional[Dict[str, Any]] = cursor.fetchone()
                if not row:
                    return None
                return cls(
                    ZYGCXX010101=row["ZYGCXX010101"],
                    JCXX010101=row["JCXX010101"],
                    ZYGFW020101=row["ZYGFW020101"],
                    ZYGFW020102=row["ZYGFW020102"],
                    ZYGFW020103=row["ZYGFW020103"],
                    ZYGFW020104=row["ZYGFW020104"],
                    ZYGFW020105=row.get("ZYGFW020105"),
                    GZFW040208=row.get("GZFW040208"),
                    ZYGCXX01018=row["ZYGCXX01018"],
                )
        except Exception as e:
            print(f"Query failed: {e}")
            return None

    @classmethod
    def list(cls, limit: int = 100, offset: int = 0, db: Optional[DataCenterMindMySQLConnector] = None) -> List["ODS_ZXSWSBLJ"]:
        connector = db or DataCenterMindMySQLConnector()
        if connector.connection is None:
            connector.connect()
        sql = f"SELECT * FROM {cls.TABLE_NAME} ORDER BY {cls.PK} LIMIT %s OFFSET %s"
        try:
            with connector.connection.cursor() as cursor:
                cursor.execute(sql, (limit, offset))
                rows = cursor.fetchall() or []
                return [
                    cls(
                        ZYGCXX010101=r["ZYGCXX010101"],
                        JCXX010101=r["JCXX010101"],
                        ZYGFW020101=r["ZYGFW020101"],
                        ZYGFW020102=r["ZYGFW020102"],
                        ZYGFW020103=r["ZYGFW020103"],
                        ZYGFW020104=r["ZYGFW020104"],
                        ZYGFW020105=r.get("ZYGFW020105"),
                        GZFW040208=r.get("GZFW040208"),
                        ZYGCXX01018=r["ZYGCXX01018"],
                    )
                    for r in rows
                ]
        except Exception as e:
            print(f"List failed: {e}")
            return []
