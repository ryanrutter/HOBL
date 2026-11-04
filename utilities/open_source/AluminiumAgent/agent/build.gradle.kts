// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.microsoft.hobl.agent"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.microsoft.hobl.agent"
        minSdk = 30
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }

    buildFeatures {
        buildConfig = true
    }

    buildTypes {
        // The agent is never installed.  It is pushed to the DUT and launched with app_process,
        // so the release APK is left unsigned.
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    testImplementation("junit:junit:4.13.2")
    // android.jar only contains stubs of org.json, so unit tests need the real implementation.
    testImplementation("org.json:json:20240303")
}

tasks.withType<Test>().configureEach {
    // Set by HOBL's Python contract tests (tests/aluminium) to host the agent's RPC server in the unit test JVM.
    System.getenv("HOBL_AGENT_CONTRACT_DIR")?.let { environment("HOBL_AGENT_CONTRACT_DIR", it) }
}
