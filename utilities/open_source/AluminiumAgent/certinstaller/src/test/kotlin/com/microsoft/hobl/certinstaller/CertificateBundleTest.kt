// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.certinstaller

import org.junit.Assert.assertTrue
import org.junit.Test

class CertificateBundleTest {
    @Test
    fun `bundled certificates are certificate authorities`() {
        for (fileName in CertificateBundle.certificateFiles) {
            val stream = javaClass.classLoader!!.getResourceAsStream(fileName)
                ?: error("Missing bundled certificate: $fileName")
            val certificate = CertificateBundle.decode(stream)
            assertTrue("$fileName is not a CA certificate", certificate.basicConstraints >= 0)
        }
    }
}
