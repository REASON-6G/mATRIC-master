import Image from "next/image";

export default function Logo() {
  return (
    <Image
      src="/logo.png"
      alt="Logo"
      width={128} // set some width
      height={32} // and height
      className="h-8 w-auto"
      priority // optional: preload if it’s always visible
    />
  );
}