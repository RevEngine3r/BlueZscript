package com.revengine3r.bluezscript.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.revengine3r.bluezscript.data.local.dao.PairedDeviceDao
import com.revengine3r.bluezscript.data.local.entity.PairedDeviceEntity

/**
 * Room database for BlueZscript.
 * Stores paired device information locally.
 */
@Database(
    entities = [PairedDeviceEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun pairedDeviceDao(): PairedDeviceDao
    
    companion object {
        const val DATABASE_NAME = "bluezscript_db"
    }
}
