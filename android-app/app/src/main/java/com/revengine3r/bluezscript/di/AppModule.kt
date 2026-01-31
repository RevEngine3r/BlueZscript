package com.revengine3r.bluezscript.di

import android.content.Context
import androidx.room.Room
import com.revengine3r.bluezscript.data.local.AppDatabase
import com.revengine3r.bluezscript.data.repository.DeviceRepository
import com.revengine3r.bluezscript.data.repository.DeviceRepositoryImpl
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Hilt module providing app-wide dependencies.
 */
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    
    @Provides
    @Singleton
    fun provideAppDatabase(
        @ApplicationContext context: Context
    ): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            AppDatabase.DATABASE_NAME
        ).build()
    }
    
    @Provides
    @Singleton
    fun providePairedDeviceDao(
        database: AppDatabase
    ) = database.pairedDeviceDao()
    
    @Provides
    @Singleton
    fun provideDeviceRepository(
        database: AppDatabase
    ): DeviceRepository {
        return DeviceRepositoryImpl(database)
    }
}
