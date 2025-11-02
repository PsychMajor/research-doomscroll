#!/usr/bin/env python3
"""
Database migration script to add folders column to profiles table
Run this manually on Render or locally to migrate the database
"""
import os
import asyncio
import asyncpg

DATABASE_URL = os.environ.get("DATABASE_URL")

async def migrate():
    """Run database migration"""
    if not DATABASE_URL:
        print("❌ No DATABASE_URL environment variable found")
        return
    
    print(f"🔄 Connecting to database...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check if folders column exists
        check_query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='profiles' AND column_name='folders'
        """
        result = await conn.fetchval(check_query)
        
        if result:
            print("✅ 'folders' column already exists in profiles table")
        else:
            print("🔄 Adding 'folders' column to profiles table...")
            await conn.execute("""
                ALTER TABLE profiles 
                ADD COLUMN folders JSONB DEFAULT '[]'::jsonb
            """)
            print("✅ 'folders' column added successfully")
        
        # Verify the column exists
        verify_query = """
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name='profiles' AND column_name='folders'
        """
        column_info = await conn.fetchrow(verify_query)
        if column_info:
            print(f"✅ Verification: folders column exists")
            print(f"   Type: {column_info['data_type']}")
            print(f"   Default: {column_info['column_default']}")
        else:
            print("❌ Verification failed: folders column not found")
        
        # Update any NULL folders to default value
        print("🔄 Updating NULL folders to default value...")
        updated = await conn.execute("""
            UPDATE profiles 
            SET folders = '[{"name": "Likes", "id": "likes"}]'::jsonb
            WHERE folders IS NULL
        """)
        print(f"✅ Updated {updated} rows with NULL folders")
        
        await conn.close()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(migrate())
